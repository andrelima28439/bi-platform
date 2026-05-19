import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from .config import settings
from .database import init_db
from .routes import analytics_router, export_router, ws_router
from .websocket import periodic_updates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting BI Analytics Platform...")
    init_db()
    logger.info("Database tables initialized")
    task = asyncio.create_task(periodic_updates())
    yield
    task.cancel()
    logger.info("Shutting down BI Analytics Platform...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="BI and Analytics Platform API - Comprehensive business intelligence endpoints",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics_router)
app.include_router(export_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}
