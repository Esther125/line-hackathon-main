"""FastAPI entrypoint wiring all Cony experiences."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers import frontend, info, line

app = FastAPI(title="Cony LINE Friend")
settings = get_settings()
app.state.default_user_id = settings.default_user_id
app.include_router(line.router)
app.include_router(info.router)
app.include_router(frontend.router)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/health")
async def healthcheck() -> dict:
    """Basic readiness probe."""

    return {"status": "ok"}
