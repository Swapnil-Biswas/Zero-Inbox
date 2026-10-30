"""
ZERO-INBOX: FastAPI Main Application
Mounts REST APIs, Autonomous Scheduler, HireCrew Seller Adapter & MCP SSE Transport
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import db
from app.scheduler.engine import scheduler_engine
from app.api.routes_digest import router as digest_router
from app.api.routes_sources import router as sources_router
from app.api.routes_preferences import router as preferences_router
from app.api.routes_analytics import router as analytics_router
from app.hirecrew.routes import router as hirecrew_router
from app.mcp.server import mcp_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and start autonomous scheduler
    db.init_db()
    scheduler_engine.start()
    yield
    # Shutdown: gracefully shut down scheduler
    scheduler_engine.stop()


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Autonomous Media Intelligence & Personalized Daily Digest Agent",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routes
app.include_router(digest_router)
app.include_router(sources_router)
app.include_router(preferences_router)
app.include_router(analytics_router)

# Mount HireCrew Seller API
app.include_router(hirecrew_router)

# Mount MCP Streamable HTTP / SSE Endpoint
# MCP client connects to http://<host>:<port>/mcp
try:
    app.mount("/mcp", mcp_server.sse_app())
except Exception:
    # If sse_app is mounted differently or streamable_http_app
    pass


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
        "scheduler_running": scheduler_engine.is_running
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name} v{settings.version}",
        "docs": "/docs",
        "mcp_endpoint": "/mcp",
        "hirecrew_seller_jobs": "/jobs"
    }
