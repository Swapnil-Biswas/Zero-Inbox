"""
ZERO-INBOX: HireCrew Seller API v1 Endpoints (/jobs)
"""

import secrets
import re
from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional
from app.core.config import settings
from app.hirecrew.models import (
    HireCrewJobSubmitRequest, HireCrewJobSubmitResponse, HireCrewJobPollResponse
)
from app.hirecrew.worker import create_or_reuse_hirecrew_job, get_job as load_job


router = APIRouter(tags=["HireCrew Seller API"])


def verify_hirecrew_auth(authorization: Optional[str] = Header(None)):
    """Enforces constant-time Bearer token authentication."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header."
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'."
        )

    token = parts[1]
    if not secrets.compare_digest(token, settings.hirecrew_seller_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid HireCrew seller authentication token."
        )


@router.post(
    "/jobs",
    response_model=HireCrewJobSubmitResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit HireCrew Seller Job"
)
async def submit_job(
    request: HireCrewJobSubmitRequest,
    authorization: Optional[str] = Header(None),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    verify_hirecrew_auth(authorization)
    if not idempotency_key or not idempotency_key.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required Idempotency-Key header.")

    try:
        job_id, job_status, is_reused = create_or_reuse_hirecrew_job(request, idempotency_key.strip())
        return HireCrewJobSubmitResponse(jobId=job_id, status=job_status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Job could not be created.")


@router.get(
    "/jobs/{job_id}",
    response_model=HireCrewJobPollResponse,
    status_code=status.HTTP_200_OK,
    summary="Poll HireCrew Seller Job Status"
)
async def get_job(
    job_id: str,
    authorization: Optional[str] = Header(None)
):
    verify_hirecrew_auth(authorization)

    if not re.match(r"^[a-zA-Z0-9_\-]+$", job_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid job ID format.")

    record = load_job(job_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return HireCrewJobPollResponse(
        jobId=record["job_id"],
        orderId=record["order_id"],
        status=record["status"],
        report=record.get("report"),
        sources=record.get("sources"),
        error=record.get("error")
    )

