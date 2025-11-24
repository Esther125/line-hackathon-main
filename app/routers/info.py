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
        "性格活潑外向、熱情可愛，總是第一個帶起氣氛",
        "超愛跳舞與甜點，剛解鎖熱門的「上車舞」",
        "粉紅色控，連舞台服飾與手機殼都要粉嫩嫩",
        "標誌是白色兔子髮箍，讓大家一眼就認出她",
    ]
    items = "".join(f"<li>{trait}</li>" for trait in traits)
    return f"""
    <section>
        <h1>About Cony</h1>
        <p>Cony 是以 LINE FRIENDS 中的兔兔延伸發想創造出的可愛少女，對兔子與粉紅色物件完全沒有抵抗力。</p>
        <ul>{items}</ul>
        <p>她熱愛表演，也總在甜點桌旁和舞池裡來回穿梭，戴著白色兔子髮箍散播元氣。</p>
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
