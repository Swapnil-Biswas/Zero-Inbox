"""
ZERO-INBOX: HireCrew Seller Job Worker

Jobs are persisted in SQLite so polling survives restarts. Each brief is answered by
the source-grounded research engine (app/hirecrew/research.py); no canned answers are
used, and buyer jobs never trigger the owner's personal digest or delivery channels.
"""

import asyncio
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set, Tuple

from app.core.config import settings
from app.hirecrew.models import HireCrewJobSubmitRequest
from app.hirecrew.research import ResearchUnavailable, run_research

_SCHEMA = """
CREATE TABLE IF NOT EXISTS hirecrew_jobs (
    job_id TEXT PRIMARY KEY,
    idempotency_key TEXT UNIQUE,
    payload_hash TEXT NOT NULL,
    order_id TEXT NOT NULL,
    brief TEXT NOT NULL,
    status TEXT NOT NULL,
    report TEXT,
    sources TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

# Strong references so background tasks are not garbage-collected mid-run.
_RUNNING: Set[asyncio.Task] = set()


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _update(job_id: str, **fields: Any) -> None:
    fields["updated_at"] = _now()
    cols = ", ".join(f"{k} = ?" for k in fields)
    with _conn() as c:
        c.execute(f"UPDATE hirecrew_jobs SET {cols} WHERE job_id = ?", (*fields.values(), job_id))


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    with _conn() as c:
        row = c.execute("SELECT * FROM hirecrew_jobs WHERE job_id = ?", (job_id,)).fetchone()
    if not row:
        return None
    job = dict(row)
    job["sources"] = json.loads(job["sources"]) if job["sources"] else None
    return job


def create_or_reuse_hirecrew_job(
    request: HireCrewJobSubmitRequest,
    idempotency_key: Optional[str] = None
) -> Tuple[str, str, bool]:
    """
    Handles HireCrew job idempotency.
    Returns (job_id, status, is_reused). Raises ValueError on an idempotency conflict.
    """
    payload_hash = hashlib.sha256(f"{request.orderId}\x00{request.brief}".encode()).hexdigest()
    with _conn() as c:
        if idempotency_key:
            row = c.execute(
                "SELECT job_id, status, payload_hash FROM hirecrew_jobs WHERE idempotency_key = ?",
                (idempotency_key,)
            ).fetchone()
            if row:
                if row["payload_hash"] != payload_hash:
                    raise ValueError("Idempotency conflict: key already used with a different payload.")
                return row["job_id"], row["status"], True

        job_id = f"zero-inbox-job-{uuid.uuid4().hex[:12]}"
        now = _now()
        c.execute(
            "INSERT INTO hirecrew_jobs (job_id, idempotency_key, payload_hash, order_id, brief, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, 'queued', ?, ?)",
            (job_id, idempotency_key, payload_hash, request.orderId, request.brief, now, now),
        )

    task = asyncio.create_task(process_hirecrew_job_async(job_id, request.brief))
    _RUNNING.add(task)
    task.add_done_callback(_RUNNING.discard)
    return job_id, "queued", False


async def process_hirecrew_job_async(job_id: str, brief: str) -> None:
    _update(job_id, status="running")
    try:
        report, sources = await asyncio.wait_for(run_research(brief), timeout=settings.hirecrew_job_timeout_seconds)
        _update(job_id, status="delivered", report=report, sources=json.dumps(sources))
    except asyncio.TimeoutError:
        _update(job_id, status="failed", error="Research timed out before a grounded report could be produced.")
    except ResearchUnavailable as e:
        _update(job_id, status="failed", error=str(e))
    except Exception as e:  # never leave a job stuck in "running"
        _update(job_id, status="failed", error=f"Internal error: {type(e).__name__}")
