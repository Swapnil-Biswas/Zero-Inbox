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
    title: str
    url: str
    snippet: Optional[str] = None


class HireCrewResearchResult(BaseModel):
    report: str
    sources: List[HireCrewResearchSource] = Field(default_factory=list)


class HireCrewJobPollResponse(BaseModel):
    jobId: str
    orderId: str
    status: str  # queued | running | delivered | failed
    result: Optional[HireCrewResearchResult] = None
    error: Optional[str] = None
