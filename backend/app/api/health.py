import os
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    # Derive environment from whether a real DATABASE_URL has been configured.
    env = "production" if (settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL) else "development"
    data_mode = "real" if os.path.exists(os.path.join(settings.DATA_DIR, "amazon_last_mile.json")) else "synthetic_demo"
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": env,
        "data_mode": data_mode,
        "data_mode_note": (
            "Real dataset files found — production data mode."
            if data_mode == "real"
            else "Real dataset files not found in ./data/. Running in synthetic_demo mode (SYNTHETIC TEST FIXTURE). "
                 "See README Section 4 for dataset setup instructions."
        ),
    }
