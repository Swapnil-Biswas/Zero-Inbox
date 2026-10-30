"""
ZERO-INBOX: Distributed Scheduler Lock
"""

import uuid
from datetime import datetime, timedelta
from app.db.database import db


class SchedulerLock:
    """Acquires an atomic database lease to prevent concurrent workers from running duplicate digests."""

    def acquire_lock(self, lock_name: str, lease_seconds: int = 600) -> bool:
        worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        expires = now + timedelta(seconds=lease_seconds)

        with db.get_connection() as conn:
            # Clean expired locks
            conn.execute("DELETE FROM scheduler_locks WHERE lock_name = ? AND expires_at < ?", (lock_name, now.isoformat()))

            # Try inserting new lock
            try:
                conn.execute(
                    "INSERT INTO scheduler_locks (lock_name, locked_by, acquired_at, expires_at) VALUES (?, ?, ?, ?)",
                    (lock_name, worker_id, now.isoformat(), expires.isoformat())
                )
                return True
            except Exception:
                # Lock already held
                return False

    def release_lock(self, lock_name: str):
        with db.get_connection() as conn:
            conn.execute("DELETE FROM scheduler_locks WHERE lock_name = ?", (lock_name,))


scheduler_lock = SchedulerLock()
