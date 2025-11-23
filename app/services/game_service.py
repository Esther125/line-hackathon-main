"""Mini-game logic for interacting with Cony."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict

from app.services.coupon_service import CouponService

CHOICES = (
    "carrot",
    "bubble-tea",
    "marshmallow",
    "macaron",
    "strawberry-cake",
    "mochi",
)


@dataclass
class GameResult:
    player_choice: str
    cony_choice: str
    did_win: bool
    reward: Dict[str, object]


class GameService:
    """Simple guessing game service used by the /play-with-cony endpoint."""

    def __init__(self, coupon_service: CouponService) -> None:
        self._coupon_service = coupon_service

    def play_round(self, player_choice: str) -> GameResult:
        """Players win if they guess the same treat Cony secretly picked."""

        normalized_choice = player_choice.lower()
        if normalized_choice not in CHOICES:
            raise ValueError(f"Choice must be one of {', '.join(CHOICES)}")

        cony_choice = random.choice(CHOICES)
        did_win = normalized_choice == cony_choice
        if did_win:
            new_coupon = self._coupon_service.add_coupon(
                title="Cony粉紅9折券",
                description="贏得遊戲即可享受全品項9折優惠。",
            )
            reward = {
                "message": "Congrats! Here are all your coupons.",
                "coupons": self._coupon_service.list_coupons(),
                "new_coupon": new_coupon,
            }
        else:
            reward = {
                "message": "Nice try! Win to collect coupons.",
                "coupons": [],
                "new_coupon": None,
            }
        return GameResult(
            player_choice=normalized_choice,
            cony_choice=cony_choice,
            did_win=did_win,
            reward=reward,
        )
