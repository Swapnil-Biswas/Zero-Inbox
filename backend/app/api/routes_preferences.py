"""
ZERO-INBOX: REST API User Preferences Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from app.core.models import UserPreferences
from app.db.database import db
from app.scheduler.engine import scheduler_engine


router = APIRouter(prefix="/api/v1/preferences", tags=["User Preferences"])


@router.get("", response_model=UserPreferences, summary="Get Preferences")
async def get_preferences(user_id: str = Query("default_user")):
    prefs = db.get_user_preferences(user_id)
    if not prefs:
        prefs = UserPreferences(user_id=user_id)
        db.save_user_preferences(prefs)
    return prefs


@router.post("", response_model=UserPreferences, summary="Save Preferences")
async def save_preferences(prefs: UserPreferences):
    db.save_user_preferences(prefs)
    # Reschedule user's autonomous cron job
    scheduler_engine.schedule_user_job(prefs.user_id)
    return prefs

