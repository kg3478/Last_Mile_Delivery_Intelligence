import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.models.models import Route, Stop, Recommendation, AuditLog
from app.schemas.schemas import RecommendationSchema, RecommendationDecisionSchema
from app.decisions.engine import DispatchDecisionEngine
from app.ml.features import FeatureEngineer
from app.ml.eta_model import ETAPredictionModel
from app.ml.deviation_model import RouteDeviationClassifier
from app.risk.scorer import DeliveryRiskScorer

router = APIRouter(prefix="/recommendations", tags=["Recommendations & Decisions"])

eta_model = ETAPredictionModel()
dev_classifier = RouteDeviationClassifier()

@router.get("", response_model=List[RecommendationSchema])
async def list_recommendations(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Recommendation))
    recs = res.scalars().all()
    if not recs:
        # Generate initial recommendations for active routes
        r_stmt = select(Route).options(selectinload(Route.stops), selectinload(Route.driver)).limit(5)
        r_res = await db.execute(r_stmt)
        routes = r_res.scalars().all()
        for r in routes:
            feats = FeatureEngineer.extract_route_features(r, r.driver, r.stops)
            delay, late = eta_model.predict_delay(feats)
            dev = dev_classifier.predict_deviation_probability(feats)
            score, level = DeliveryRiskScorer.calculate_risk(delay, late, dev, feats["time_window_pressure"], feats["route_complexity_score"])
            
            rec = DispatchDecisionEngine.generate_recommendation(r, r.stops, score, level, delay, dev)
            db.add(rec)
        await db.commit()
        res = await db.execute(select(Recommendation))
        recs = res.scalars().all()
        
    return recs

@router.post("/decision")
async def record_recommendation_decision(req: RecommendationDecisionSchema, db: AsyncSession = Depends(get_db)):
    stmt = select(Recommendation).where(Recommendation.id == req.recommendation_id)
    res = await db.execute(stmt)
    rec = res.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = "ACCEPTED" if req.action == "ACCEPT" else ("REJECTED" if req.action == "REJECT" else "DISMISSED")

    # Record Audit Log per Section 34
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_id=req.user_id or "dispatcher_01",
        action="RECOMMENDATION_DECISION",
        entity_type="RECOMMENDATION",
        entity_id=rec.id,
        details={
            "action": req.action,
            "reason": req.reason or "Dispatcher review completed.",
            "route_id": rec.route_id,
            "risk_score": rec.risk_score,
            "recommendation_title": rec.title
        },
        timestamp=datetime.datetime.utcnow()
    )
    db.add(audit)
    await db.commit()

    return {"status": "SUCCESS", "recommendation_id": rec.id, "new_status": rec.status}
