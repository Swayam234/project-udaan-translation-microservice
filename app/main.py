"""
app/main.py

FastAPI application factory.

Responsibilities
----------------
- Create and configure the FastAPI application instance.
- Register all routers.
- Configure global exception handlers.
- Initialise the database on startup.
- Add CORS and request-timing middleware.
"""

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config.settings import get_settings
from app.database.connection import init_db
from app.routes import health as health_router
from app.routes import translate as translate_router
from app.routes import logs as logs_router
from app.utils.logger import setup_logging

# Initialise logging before anything else
setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager executed by FastAPI on startup and shutdown.
    Replaces the deprecated @app.on_event("startup") pattern.
    """
    # Startup
    logger.info("-" * 60)
    logger.info("  %s  v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("-" * 60)
    init_db()
    logger.info("Server running at  -->  http://localhost:%s", settings.PORT)
    logger.info("Swagger UI         -->  http://localhost:%s/docs", settings.PORT)
    logger.info("Health check       -->  http://localhost:%s/health", settings.PORT)
    logger.info("-" * 60)
    yield
    # Shutdown
    logger.info("Application shutting down...")


# ── Application factory ────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Construct and return the configured FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],          # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request timing middleware ──────────────────────────────────────────
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """Attach X-Process-Time-Ms header to every response."""
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
        return response

    # ── Global exception handlers ──────────────────────────────────────────

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Return a structured JSON error for Pydantic validation failures.

        Pydantic v2 error dicts may contain non-serialisable objects (e.g. ValueError
        instances in the 'ctx' field).  We serialise them to strings before building
        the JSONResponse to avoid a TypeError at the json.dumps() stage.
        """
        import json as _json

        def _make_serialisable(obj):
            """Recursively convert non-JSON-serialisable objects to strings."""
            if isinstance(obj, dict):
                return {k: _make_serialisable(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [_make_serialisable(i) for i in obj]
            try:
                _json.dumps(obj)   # probe serialisability
                return obj
            except (TypeError, ValueError):
                return str(obj)

        errors = _make_serialisable(exc.errors())
        logger.warning("Validation error on %s: %s", request.url.path, errors)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "Request validation failed.",
                "detail": errors,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Catch-all handler for unhandled exceptions."""
        logger.exception("Unhandled exception on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "An unexpected internal server error occurred.",
                "detail": str(exc) if settings.DEBUG else None,
            },
        )

    # ── Routers ────────────────────────────────────────────────────────────
    app.include_router(health_router.router)
    app.include_router(translate_router.router)
    app.include_router(logs_router.router)

    # ── Root redirect ──────────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
        }

    return app


# ── Application instance (imported by uvicorn) ─────────────────────────────────
app = create_app()
