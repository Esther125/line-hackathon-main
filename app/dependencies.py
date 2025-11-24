"""Dependencies for FastAPI routes."""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
from sqlalchemy.orm import Session

from app.services.chat_service import ConyChatService
from app.services.coupon_service import CouponService
from app.services.game_service import GameService
from database.session import create_session_factory


@lru_cache
def _chat_service(
    api_key: str,
    api_base: str,
    user_id: str | None,
    app_title: str | None,
) -> ConyChatService:
    return ConyChatService(
        api_key=api_key,
        api_base=api_base,
        user_id=user_id,
        app_title=app_title,
    )


@lru_cache
def _session_factory(database_url: str):
    return create_session_factory(database_url)


def get_db(settings: Settings = Depends(get_settings)) -> Session:
    SessionLocal = _session_factory(settings.database_url)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_chat_service(
    settings: Settings = Depends(get_settings),
) -> ConyChatService:
    """Provide a singleton chat service configured with the OpenAI key."""

    return _chat_service(
        settings.openai_api_key,
        settings.openai_api_base,
        settings.openai_user_id,
        settings.openai_app_title,
    )


def get_coupon_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> CouponService:
    """Provide a coupon service backed by the Postgres database."""

    return CouponService(
        session=db,
        default_user_id=settings.default_user_id,
    )


def get_game_service(
    coupon_service: CouponService = Depends(get_coupon_service),
) -> GameService:
    """Provide a game service that shares the coupon catalog."""

    return GameService(coupon_service=coupon_service)
