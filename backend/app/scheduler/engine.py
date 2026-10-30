"""
ZERO-INBOX: Autonomous APScheduler Engine (Timezone-Aware Cron)
"""

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional
from app.db.database import db
from app.scheduler.runner import run_user_digest_pipeline


class SchedulingEngine:
    """Manages timezone-aware automated daily cron jobs for all registered users."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            self.reload_all_user_schedules()

    def stop(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False

    def schedule_user_job(self, user_id: str = "default_user"):
        """Schedules or updates the daily morning digest trigger for a user."""
        prefs = db.get_user_preferences(user_id)
        if not prefs:
            return

        job_id = f"daily_digest_{user_id}"

        # Resolve timezone safely
        try:
            tz = pytz.timezone(prefs.timezone)
        except Exception:
            tz = pytz.UTC

        trigger = CronTrigger(
            hour=prefs.delivery_time_hour,
            minute=prefs.delivery_time_minute,
            timezone=tz
        )

        # Remove existing if present
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            run_user_digest_pipeline,
            trigger=trigger,
            id=job_id,
            args=[user_id, False],
            name=f"Daily Media Digest for {user_id} at {prefs.delivery_time_hour:02d}:{prefs.delivery_time_minute:02d} ({prefs.timezone})",
            replace_existing=True
        )

    def reload_all_user_schedules(self):
        # Default user schedule
        self.schedule_user_job("default_user")

    def get_job_info(self, user_id: str = "default_user") -> Optional[dict]:
        job = self.scheduler.get_job(f"daily_digest_{user_id}")
        if not job:
            return None
        return {
            "job_id": job.id,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "name": job.name
        }


scheduler_engine = SchedulingEngine()
