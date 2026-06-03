"""
SmartCart AI - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base
from app.routers import (
    products,
    prices,
    forecasts,
    recommendations,
    basket,
    analytics,
    assistant,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting SmartCart AI backend...")
    # Tables are created via SQL migrations, but create if missing in dev
    async with engine.begin() as conn:
        pass  # Schema managed by sql/ files
    logger.info("SmartCart AI backend started successfully.")
    yield
    logger.info("Shutting down SmartCart AI backend...")


app = FastAPI(
    title="SmartCart AI",
    description="Grocery Price Intelligence Platform — track, forecast, and optimize grocery spending.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(prices.router, prefix="/api/prices", tags=["Prices"])
app.include_router(forecasts.router, prefix="/api/forecasts", tags=["Forecasts"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(basket.router, prefix="/api/basket", tags=["Basket"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["AI Assistant"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "SmartCart AI",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "environment": settings.environment}
