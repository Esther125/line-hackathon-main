"""Service that manages coupons earned from games with Cony."""
from __future__ import annotations

from typing import Dict, List


class CouponService:
    """Provides simple in-memory coupon operations for demo purposes."""

    def __init__(self) -> None:
        self._catalog: List[Dict[str, str]] = [
            {
                "id": "brunch-001",
                "title": "Brunch with Brown",
                "description": "Buy one get one carrot croissant at Brown's Cafe.",
            },
            {
                "id": "dessert-007",
                "title": "Bubble Tea Upgrade",
                "description": "Free topping upgrade when you order milk tea.",
            },
            {
                "id": "fashion-042",
                "title": "Cony Style Boost",
                "description": "10% off any pink outfit in LINE FRIENDS store.",
            },
        ]
        self._counter = 100

    def list_coupons(self) -> List[Dict[str, str]]:
        """Return all demo coupons."""

        return self._catalog.copy()

    def all_coupon_ids(self) -> List[str]:
        """Return coupon ids for quick references."""

        return [coupon["id"] for coupon in self._catalog]

    def add_coupon(self, title: str, description: str) -> Dict[str, str]:
        """Create and store a new coupon when players win games."""

        self._counter += 1
        coupon = {
            "id": f"cony-{self._counter}",
            "title": title,
            "description": description,
        }
        self._catalog.append(coupon)
        return coupon
