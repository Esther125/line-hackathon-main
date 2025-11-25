"""Dependencies for FastAPI routes."""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.services.coupon_service import CouponService
from app.services.game_service import GameService
from app.services.line_chat_service import LineChatService
from app.services.web_chat_service import WebChatService
from database.session import create_session_factory


@lru_cache
def _web_chat_service(
    api_key: str,
    api_base: str,
    user_id: str | None,
    app_title: str | None,
) -> WebChatService:
    return WebChatService(
        api_key=api_key,
        api_base=api_base,
        user_id=user_id,
        app_title=app_title,
    )


@lru_cache
def _line_chat_service(
    api_key: str,
    api_base: str,
    user_id: str | None,
    app_title: str | None,
) -> LineChatService:
    return LineChatService(
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


def get_web_chat_service(
    settings: Settings = Depends(get_settings),
) -> WebChatService:
    """Provide a singleton chat service configured with the OpenAI key."""

    return _web_chat_service(
        settings.openai_api_key,
        settings.openai_api_base,
        settings.openai_user_id,
        settings.openai_app_title,
    )


def get_line_chat_service(
    settings: Settings = Depends(get_settings),
) -> LineChatService:
    return _line_chat_service(
        settings.openai_api_key,
        settings.openai_api_base,
        settings.openai_user_id,
        settings.openai_app_title,
    )


def get_current_user_id(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> str:
    """Determine the user id from cookies or fallback to default."""

    user_id = request.cookies.get("cony_user_id")
    if user_id:
        request.state.current_user_id = user_id
        request.state.from_cookie = True
        return user_id
    request.state.current_user_id = settings.default_user_id
    request.state.from_cookie = False
    return settings.default_user_id


def get_coupon_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user_id: str = Depends(get_current_user_id),
) -> CouponService:
    """Provide a coupon service backed by the Postgres database."""

    return CouponService(
        session=db,
        default_user_id=user_id,
    )


def get_game_service(
    coupon_service: CouponService = Depends(get_coupon_service),
) -> GameService:
    """Provide a game service that shares the coupon catalog."""

    return GameService(coupon_service=coupon_service)
