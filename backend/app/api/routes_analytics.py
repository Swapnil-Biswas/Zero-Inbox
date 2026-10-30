"""
ZERO-INBOX: REST API Cost & Operational Analytics Endpoints
"""

from fastapi import APIRouter, Query
from app.db.database import db
from app.scheduler.engine import scheduler_engine


router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Health"])


@router.get("/costs", summary="Get Token and USD Cost Summary")
async def get_costs(user_id: str = Query("default_user")):
    return db.get_cost_summary(user_id)


@router.get("/overview", summary="Get Operational Overview")
async def get_overview(user_id: str = Query("default_user")):
    sources = db.list_sources(user_id=user_id)
    costs = db.get_cost_summary(user_id=user_id)
    latest_digest = db.get_latest_digest(user_id=user_id)
    sched = scheduler_engine.get_job_info(user_id=user_id)

    return {
        "active_sources_count": len([s for s in sources if s.status == "active"]),
        "total_sources_count": len(sources),
        "total_spent_usd": costs.get("total_spent_usd", 0.0),
        "total_tokens_consumed": costs.get("total_tokens", 0),
        "latest_digest_date": latest_digest.date_str if latest_digest else None,
        "next_scheduled_execution": sched.get("next_run_time") if sched else None
    }
