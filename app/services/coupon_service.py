"""Service that manages coupons earned from games with Cony."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Sequence

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "coupons.json"


class CouponService:
    """Provides file-backed coupon operations for demo purposes."""

    def __init__(self, data_path: str | Path | None = None) -> None:
        self._data_path = Path(data_path) if data_path else DEFAULT_DATA_PATH
        self._data_path.parent.mkdir(parents=True, exist_ok=True)
        self._catalog: List[Dict[str, str]] = self._load_catalog()
        self._counter = self._derive_initial_counter(self._catalog)

    def _load_catalog(self) -> List[Dict[str, str]]:
        if self._data_path.exists():
            raw = self._data_path.read_text(encoding="utf-8")
            data = json.loads(raw or "[]")
            if isinstance(data, list):
                catalog: List[Dict[str, str]] = []
                for item in data:
                    normalized = dict(item)
                    if "source" not in normalized:
                        normalized["source"] = "catalog"
                    catalog.append(normalized)
                return catalog
            raise ValueError(f"Coupon data must be a list, got {type(data)}")

        self._data_path.write_text("[]", encoding="utf-8")
        return []

    def _save_catalog(self) -> None:
        payload = json.dumps(self._catalog, ensure_ascii=False, indent=2)
        self._data_path.write_text(payload + "\n", encoding="utf-8")

    @staticmethod
    def _derive_initial_counter(catalog: Sequence[Dict[str, str]]) -> int:
        counter = 100
        for coupon in catalog:
            coupon_id = coupon.get("id", "")
            if coupon_id.startswith("cony-"):
                suffix = coupon_id.split("-", 1)[1]
                if suffix.isdigit():
                    counter = max(counter, int(suffix))
        return counter

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
            "source": "game",
        }
        self._catalog.append(coupon)
        self._save_catalog()
        return coupon
