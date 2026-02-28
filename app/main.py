"""GACMS - Group Asset Custody Management System. Main FastAPI app."""

from contextlib import asynccontextmanager
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging_config import setup_logging
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.groups.router import router as groups_router
from app.modules.companies.router import router as companies_router
from app.modules.branches.router import router as branches_router
from app.modules.employees.router import router as employees_router
from app.modules.assets.router import router as assets_router
from app.modules.scan.router import router as scan_router
from app.modules.documents.router import router as documents_router
from app.modules.audits.router import router as audits_router
from app.modules.logs.router import router as logs_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.alerts.router import router as alerts_router
from app.modules.bulk_import.router import router as bulk_import_router
from app.modules.search.router import router as search_router
from app.modules.backup.router import router as backup_router


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-related headers to all responses."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="STC GACMS",
        description="Group Asset Custody Management System - Internal SaaS",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail if isinstance(exc.detail, str) else exc.detail},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api_prefix = "/api/v1"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(users_router, prefix=api_prefix)
    app.include_router(groups_router, prefix=api_prefix)
    app.include_router(companies_router, prefix=api_prefix)
    app.include_router(branches_router, prefix=api_prefix)
    app.include_router(employees_router, prefix=api_prefix)
    app.include_router(assets_router, prefix=api_prefix)
    app.include_router(documents_router, prefix=api_prefix)
    app.include_router(audits_router, prefix=api_prefix)
    app.include_router(logs_router, prefix=api_prefix)
    app.include_router(dashboard_router, prefix=api_prefix)
    app.include_router(alerts_router, prefix=api_prefix)
    app.include_router(bulk_import_router, prefix=api_prefix)
    app.include_router(search_router, prefix=api_prefix)
    app.include_router(backup_router, prefix=api_prefix)
    # Public scan (no auth) - mount at root so /scan/{uuid} works for QR
    app.include_router(scan_router, prefix="")
    # Uploads (logos, etc.) - serve at /uploads
    upload_dir = Path(settings.upload_dir).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")
    # Static files (frontend)
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    return app


app = create_app()

# Serve SPA frontend (Arabic UI) at root
static_index = Path(__file__).resolve().parent.parent / "static" / "index.html"


@app.get("/")
def index():
    """الواجهة الأمامية بالعربية (خط الإسكندرية)."""
    if static_index.exists():
        return FileResponse(static_index)
    return {"message": "STC GACMS API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
