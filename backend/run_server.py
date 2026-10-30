"""
ZERO-INBOX: Backend Server Launcher
"""

import uvicorn
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings


if __name__ == "__main__":
    print(f"Starting {settings.app_name} on {settings.host}:{settings.port}...")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

