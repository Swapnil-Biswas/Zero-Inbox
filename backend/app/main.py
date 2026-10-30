"""
ZERO-INBOX: FastAPI Main Application
Mounts REST APIs, Autonomous Scheduler, HireCrew Seller Adapter & MCP SSE Transport
"""

import secrets

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.responses import JSONResponse

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
    # Mounted sub-apps get no lifespan of their own, so run the MCP session manager here.
    async with mcp_server.session_manager.run():
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
    allow_credentials=False,
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

# MCP Streamable HTTP endpoint (POST /mcp). Its tools can change sources and send
# notifications, so set ZERO_INBOX_MCP_AUTH_TOKEN before exposing it beyond localhost.
mcp_http_app = mcp_server.streamable_http_app(streamable_http_path="/mcp", stateless_http=True, json_response=True)


@app.middleware("http")
async def require_mcp_token(request, call_next):
    if request.url.path.startswith("/mcp") and settings.mcp_auth_token:
        supplied = request.headers.get("authorization", "")
        if not secrets.compare_digest(supplied, f"Bearer {settings.mcp_auth_token}"):
            return JSONResponse({"detail": "Invalid or missing MCP bearer token."}, status_code=401)
    return await call_next(request)


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


# Must stay the last route registered: serves POST /mcp without a redirect.
app.mount("/", mcp_http_app)
