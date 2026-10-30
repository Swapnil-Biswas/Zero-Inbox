"""
ZERO-INBOX: REST API Source Management Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.core.models import SourceConfig
from app.db.database import db
from app.ingestion.manager import ingestion_manager


router = APIRouter(prefix="/api/v1/sources", tags=["Source Management"])


@router.get("", response_model=List[SourceConfig], summary="List Configured Sources")
async def list_sources(
    user_id: str = Query("default_user"),
    status: Optional[str] = Query(None)
):
    return db.list_sources(user_id=user_id, status=status)


@router.post("", response_model=SourceConfig, summary="Add New Source")
async def add_source(source: SourceConfig):
    # Validate connector configuration
    connector = ingestion_manager.get_connector(source.source_type)
    is_valid, err = connector.validate_configuration(source)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Source validation error: {err}")

    created = db.add_source(source)
    return created


@router.delete("/{source_id}", summary="Remove Source")
async def remove_source(
    source_id: str,
    user_id: str = Query("default_user")
):
    success = db.remove_source(source_id=source_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Source not found.")
    return {"status": "success", "message": f"Source {source_id} removed."}


@router.post("/{source_id}/test", summary="Test Ingesting Source")
async def test_source_fetch(
    source_id: str,
    user_id: str = Query("default_user")
):
    source = db.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found.")

    articles = await ingestion_manager.ingest_source(source)
    return {
        "status": "success",
        "articles_found": len(articles),
        "sample_titles": [a.title for a in articles[:3]]
    }
