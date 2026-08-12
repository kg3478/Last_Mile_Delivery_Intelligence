from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any

from app.core.database import get_db
from app.models.models import Route, Delivery, Driver, Stop, Prediction
from app.schemas.schemas import RiskPredictionRequestSchema, OverviewAnalyticsSchema
from app.ml.features import FeatureEngineer
from app.ml.eta_model import ETAPredictionModel
from app.ml.deviation_model import RouteDeviationClassifier
from app.risk.scorer import DeliveryRiskScorer
from app.analytics.delivery import DeliveryAnalytics

router = APIRouter(tags=["Deliveries & Risk"])

eta_model = ETAPredictionModel()
dev_classifier = RouteDeviationClassifier()

@router.get("/overview", response_model=OverviewAnalyticsSchema)
async def get_overview_analytics(db: AsyncSession = Depends(get_db)):
    return await DeliveryAnalytics.compute_overview_kpis(db)

@router.get("/deliveries")
async def list_deliveries(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Delivery).limit(100))
    return res.scalars().all()

@router.post("/routes/predict-risk")
async def predict_route_risk(req: RiskPredictionRequestSchema, db: AsyncSession = Depends(get_db)):
    stmt = select(Route).where(Route.id == req.route_id).options(
        selectinload(Route.stops)
    )
    res = await db.execute(stmt)
    route = res.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Load driver separately
    driver = None
    if route.driver_id:
        d_res = await db.execute(select(Driver).where(Driver.id == route.driver_id))
        driver = d_res.scalar_one_or_none()

    stops = route.stops

    features = FeatureEngineer.extract_route_features(route, driver, stops)
    pred_delay, late_prob = eta_model.predict_delay(features)
    dev_prob = dev_classifier.predict_deviation_probability(features)

    risk_score, risk_level = DeliveryRiskScorer.calculate_risk(
        pred_delay, late_prob, dev_prob,
        features["time_window_pressure"],
        features["route_complexity_score"]
    )

    return {
        "route_id": route.id,
        "external_route_id": route.external_route_id,
        "predicted_delay_min": pred_delay,
        "late_probability": late_prob,
        "deviation_probability": dev_prob,
        "composite_risk_score": risk_score,
        "risk_level": risk_level,
        "features": features
    }
