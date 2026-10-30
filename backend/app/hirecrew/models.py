"""
ZERO-INBOX: HireCrew Seller API v1 Pydantic Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class HireCrewJobSubmitRequest(BaseModel):
    orderId: str = Field(..., min_length=1, max_length=128)
    brief: str = Field(..., min_length=1, max_length=50000)
    buyerId: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class HireCrewJobSubmitResponse(BaseModel):
    jobId: str
    status: str = "queued"


class HireCrewResearchSource(BaseModel):
    """HireCrew validates sources strictly: exactly {title, url}."""
    title: str
    url: str


class HireCrewJobPollResponse(BaseModel):
    """seller-hosted-api-v1: report and sources are top-level fields of a delivered job."""
    jobId: str
    orderId: str
    status: str  # queued | running | delivered | failed
    report: Optional[str] = None
    sources: Optional[List[HireCrewResearchSource]] = None
    error: Optional[str] = None
