from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.ingestion.pipeline import IngestionPipeline
from app.schemas.schemas import IngestRequestSchema

from app.api import (
    health, datasets, routes, deliveries,
    optimization, recommendations, drivers, models, audit
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    await init_db()
    
    # Check if database has initial sample data, if not load fixture data automatically
    async with AsyncSessionLocal() as session:
        pipeline = IngestionPipeline(session)
        # Load sample datasets so app is immediately interactive out-of-the-box
        try:
            await pipeline.run_ingestion(IngestRequestSchema(dataset_name="AMAZON_LAST_MILE"))
            await pipeline.run_ingestion(IngestRequestSchema(dataset_name="MENDELEY_PLANNED_VS_ACTUAL"))
        except Exception as e:
            print(f"Initial ingestion notice: {e}")
            
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health.router)
app.include_router(datasets.router, prefix=settings.API_V1_STR)
app.include_router(routes.router, prefix=settings.API_V1_STR)
app.include_router(deliveries.router, prefix=settings.API_V1_STR)
app.include_router(optimization.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)
app.include_router(drivers.router, prefix=settings.API_V1_STR)
app.include_router(models.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
