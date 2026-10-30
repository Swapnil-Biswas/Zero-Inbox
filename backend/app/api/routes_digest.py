"""
ZERO-INBOX: REST API Digest Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.core.models import Digest
from app.db.database import db
from app.scheduler.runner import run_user_digest_pipeline


router = APIRouter(prefix="/api/v1/digest", tags=["Digest Operations"])


@router.post("/generate", response_model=Digest, summary="Generate On-Demand Daily Digest")
async def trigger_digest_generation(
    user_id: str = Query("default_user"),
    force: bool = Query(True)
):
    digest = await run_user_digest_pipeline(user_id=user_id, force=force)
    if not digest:
        raise HTTPException(status_code=500, detail="Failed to synthesize daily digest.")
    return digest


@router.get("/latest", response_model=Digest, summary="Get Most Recent Digest")
async def get_latest_digest(user_id: str = Query("default_user")):
    digest = db.get_latest_digest(user_id)
    if not digest:
        raise HTTPException(status_code=404, detail="No digest found.")
    return digest


@router.get("/history", response_model=List[Digest], summary="Get Historical Digests")
async def get_digest_history(
    user_id: str = Query("default_user"),
    limit: int = Query(15, ge=1, le=100)
):
    return db.get_digest_history(user_id=user_id, limit=limit)

