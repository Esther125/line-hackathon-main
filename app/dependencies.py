"""Dependencies for FastAPI routes."""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
from app.services.chat_service import ConyChatService
from app.services.coupon_service import CouponService
from app.services.game_service import GameService


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
def _coupon_service() -> CouponService:
    return CouponService()


@lru_cache
def _game_service(coupon_service: CouponService) -> GameService:
    return GameService(coupon_service=coupon_service)


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


def get_coupon_service() -> CouponService:
    """Provide an in-memory coupon service."""

    return _coupon_service()


def get_game_service() -> GameService:
    """Provide a singleton game service that shares the coupon catalog."""

    return _game_service(_coupon_service())
