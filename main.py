"""
main.py (project root)

Entry point for running the service directly:

    python main.py

This is a convenience wrapper around uvicorn.
For production use `uvicorn app.main:app` directly.
"""

import uvicorn
from app.config.settings import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
