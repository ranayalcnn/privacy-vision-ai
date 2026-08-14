from __future__ import annotations

from contextlib import asynccontextmanager
import mimetypes

from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from api.config import PROJECT_ROOT, settings
from api.docs import themed_swagger_ui
from api.routers import forklift, jobs, people, pose, privacy
from api.schemas import HealthResponse
from api.security import enforce_api_access
from api.services.warmup import model_warmup_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    model_warmup_manager.start()
    yield


app = FastAPI(
    title=settings.title,
    version=settings.version,
    docs_url=None,
    lifespan=lifespan,
    description=(
        "KVKK odaklı yüz anonimleştirme ve depo nesnesi tespit servisi."
    ),
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(self), microphone=(), geolocation=(), payment=(), usb=()"
    )
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["X-XSS-Protection"] = "0"

    if request.url.path == "/docs":
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "connect-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'"
        )
    else:
        csp = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "font-src 'self'; img-src 'self' data: blob:; "
            "media-src 'self' blob:; connect-src 'self'; worker-src 'self' blob:; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; "
            "form-action 'self'"
        )
    response.headers["Content-Security-Policy"] = csp

    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("font/woff2", ".woff2")

api_dependencies = [Depends(enforce_api_access)]
app.include_router(privacy.router, prefix="/api/v1", dependencies=api_dependencies)
app.include_router(forklift.router, prefix="/api/v1", dependencies=api_dependencies)
app.include_router(people.router, prefix="/api/v1", dependencies=api_dependencies)
app.include_router(pose.router, prefix="/api/v1", dependencies=api_dependencies)
app.include_router(jobs.router, prefix="/api/v1", dependencies=api_dependencies)
app.mount(
    "/static",
    StaticFiles(directory=PROJECT_ROOT / "api" / "static"),
    name="static",
)


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(PROJECT_ROOT / "api" / "static" / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/docs", include_in_schema=False)
def docs() -> HTMLResponse:
    return themed_swagger_ui(app.openapi_url or "/openapi.json", f"{settings.title} · API")


@app.get("/health", response_model=HealthResponse, tags=["Sistem"])
def health() -> HealthResponse:
    return HealthResponse(status="healthy", version=settings.version)


@app.get("/health/models", tags=["Sistem"])
def model_health() -> dict:
    return model_warmup_manager.status()
