"""Routers for informational and interactive endpoints."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.dependencies import get_chat_service, get_coupon_service, get_game_service
from app.services.chat_service import ConyChatService
from app.services.coupon_service import CouponService
from app.services.game_service import CHOICES, GameResult, GameService

router = APIRouter(tags=["cony-extras"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=300)


class PlayRequest(BaseModel):
    player_choice: Literal[
        "carrot",
        "bubble-tea",
        "marshmallow",
        "macaron",
        "strawberry-cake",
        "mochi",
    ]


def _render_about_cony() -> str:
    traits = [
        "性格活潑外向，但偶爾自我中心",
        "作為熊大的女朋友，非常關心與Brown的關係",
        "愛吃美食、追求時尚，又討厭家事",
        "遇到誤會會先激動，再好好反省並解決問題",
    ]
    items = "".join(f"<li>{trait}</li>" for trait in traits)
    return f"""
    <section>
        <h1>About Cony</h1>
        <p>4月17日出生的可妮兔，是LINE FRIENDS中最活力滿滿的時尚達人。</p>
        <ul>{items}</ul>
        <p>喜歡美食、可愛事物與熊大，討厭打掃與煮飯。一起跟她冒險吧！</p>
    </section>
    """


@router.get("/about-cony", response_class=HTMLResponse)
async def about_cony() -> str:
    """Serve a short HTML snippet describing Cony's personality."""

    return _render_about_cony()


@router.get("/coupons")
async def view_coupons(coupon_service: CouponService = Depends(get_coupon_service)) -> dict:
    """Return all currently available coupons."""

    return {"coupons": coupon_service.list_coupons()}


@router.post("/chat-with-cony")
async def chat_with_cony(
    payload: ChatRequest,
    chat_service: ConyChatService = Depends(get_chat_service),
) -> dict:
    """Expose Cony's chat persona for the frontend interface."""

    reply = await chat_service.generate_reply(payload.message)
    return {"reply": reply}


@router.post("/play-with-cony")
async def play_with_cony(
    payload: PlayRequest,
    game_service: GameService = Depends(get_game_service),
) -> dict:
    """Run a guessing game round between the caller and Cony."""

    try:
        result: GameResult = game_service.play_round(payload.player_choice)
    except ValueError as exc:  # pragma: no cover - FastAPI handles validation
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "player_choice": result.player_choice,
        "cony_choice": result.cony_choice,
        "did_win": result.did_win,
        "reward": result.reward,
        "available_choices": CHOICES,
    }
