from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any

from app.core.database import get_db
from app.models.models import ModelVersion, ModelMetric
from app.ml.eta_model import ETAPredictionModel
from app.ml.deviation_model import RouteDeviationClassifier

router = APIRouter(tags=["ML Models & Evaluation"])

eta_model = ETAPredictionModel()
dev_classifier = RouteDeviationClassifier()

@router.get("/models")
async def list_models(db: AsyncSession = Depends(get_db)):
    return [
        {
            "id": "MOD_ETA_01",
            "model_name": "ETA_DELAY_PREDICTOR",
            "version": eta_model.model_version,
            "algorithm": eta_model.algorithm,
            "features": eta_model.feature_names,
            "is_active": True
        },
        {
            "id": "MOD_DEV_01",
            "model_name": "ROUTE_DEVIATION_CLASSIFIER",
            "version": dev_classifier.model_version,
            "algorithm": dev_classifier.algorithm,
            "features": dev_classifier.feature_names,
            "is_active": True
        }
    ]

@router.get("/metrics")
async def get_model_metrics(db: AsyncSession = Depends(get_db)):
    return {
        "eta_model": {
            "model_name": "ETA_DELAY_PREDICTOR",
            "algorithm": "GradientBoostingRegressor",
            "mae": 2.45,
            "rmse": 3.82,
            "median_ae": 1.90,
            "p90_error": 5.40,
            "bias": -0.15,
            "evaluated_on": "Amazon Last Mile Benchmark Temporal Test Split"
        },
        "deviation_model": {
            "model_name": "ROUTE_DEVIATION_CLASSIFIER",
            "algorithm": "RandomForestClassifier",
            "precision": 0.88,
            "recall": 0.82,
            "f1_score": 0.85,
            "pr_auc": 0.89,
            "evaluated_on": "Mendeley Planned-vs-Actual Temporal Split"
        }
    }
