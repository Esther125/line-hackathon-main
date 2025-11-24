"""Service that manages coupons earned from games with Cony."""
from __future__ import annotations

from typing import Dict, List
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import AppUser, Coupon, CouponType

class CouponService:
    """Provides Postgres-backed coupon operations."""

    def __init__(
        self,
        session: Session,
        default_user_id: str = "demo-user",
    ) -> None:
        self._session = session
        self._user_id = default_user_id
        self._ensure_user_exists()

    def _ensure_user_exists(self) -> None:
        user = self._session.scalar(select(AppUser).where(AppUser.user_id == self._user_id))
        if not user:
            user = AppUser(user_id=self._user_id)
            self._session.add(user)
            self._session.commit()

    def list_coupons(self) -> List[Dict[str, str]]:
        """Return all coupons for the default user."""

        coupons = self._session.scalars(
            select(Coupon).where(Coupon.user_id == self._user_id).order_by(Coupon.created_at.desc())
        ).all()
        results: List[Dict[str, str]] = []
        for coupon in coupons:
            results.append(
                {
                    "id": coupon.code,
                    "title": coupon.title,
                    "description": coupon.description or "",
                    "source": "game" if coupon.type == CouponType.game else "catalog",
                }
            )
        return results

    def add_coupon(self, title: str, description: str) -> Dict[str, str]:
        """Create and store a new coupon when players win games."""

        code = f"CONY-{uuid4().hex[:8].upper()}"
        coupon = Coupon(
            user_id=self._user_id,
            type=CouponType.game,
            code=code,
            title=title,
            description=description,
        )
        self._session.add(coupon)
        self._session.commit()
        return {
            "id": coupon.code,
            "title": coupon.title,
            "description": coupon.description or "",
            "source": "game",
        }

    def consume_coupon(self, code: str) -> bool:
        """Delete a coupon once the user confirms usage."""

        coupon = self._session.scalar(
            select(Coupon).where(Coupon.user_id == self._user_id, Coupon.code == code)
        )
        if not coupon:
            return False
        self._session.delete(coupon)
        self._session.commit()
        return True
