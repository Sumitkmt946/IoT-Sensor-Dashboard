"""
FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.mqtt_client import start_mqtt, stop_mqtt
from app.routers import sensor_data, alerts

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("main")


# ── Lifespan (startup / shutdown) ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables …")
    Base.metadata.create_all(bind=engine)
    logger.info("Starting MQTT subscriber …")
    start_mqtt()
    yield
    # Shutdown
    stop_mqtt()
    logger.info("Application shut down.")


# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="IoT Sensor Dashboard API",
    description="Real-time sensor data ingestion via MQTT with threshold-based alerts.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(sensor_data.router)
app.include_router(alerts.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "IoT Sensor Dashboard API"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
