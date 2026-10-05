"""FastAPI development backend for Rosas Eternas."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Deque

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    allowed_origins: str = ""
    rate_limit_per_minute: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


settings = Settings()
_requests: dict[str, Deque[float]] = defaultdict(deque)


class HealthResponse(BaseModel):
    status: str
    service: str
    message: str


class CapabilityContext(BaseModel):
    """Minimum metadata received from the mobile delivery flow."""

    locationState: str | None = None
    cameraState: str | None = None
    locationLabel: str | None = None
    photoAttached: bool = False
    updatedAt: str | None = None


class CapabilityEvent(BaseModel):
    orderId: str
    context: CapabilityContext


_capability_events: deque[CapabilityEvent] = deque(maxlen=100)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _requests.clear()
    yield
    _requests.clear()


app = FastAPI(
    title="API Rosas Eternas",
    version="1.0.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url=None,
    lifespan=lifespan,
)

if settings.origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
        max_age=600,
    )


@app.middleware("http")
async def protect_local_api(request: Request, call_next):
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = _requests[client]
    while window and now - window[0] >= 60:
        window.popleft()
    if len(window) >= settings.rate_limit_per_minute:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Demasiadas solicitudes. Intenta nuevamente en un minuto."},
            headers={"Retry-After": "60"},
        )
    window.append(now)
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/api/health", response_model=HealthResponse, tags=["diagnóstico"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="API Rosas Eternas",
        message="Solicitud móvil recibida correctamente",
    )


@app.post("/api/capability-events", status_code=status.HTTP_202_ACCEPTED, tags=["pedidos"])
async def register_capability_event(event: CapabilityEvent) -> dict[str, str]:
    """Store only delivery-capability metadata for the local demonstration.

    No image bytes or precise coordinates are accepted by this endpoint.
    """
    _capability_events.append(event)
    return {"status": "accepted"}
