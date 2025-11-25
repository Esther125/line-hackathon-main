"""Shared chat service utilities for Cony experiences."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List, Optional

import requests
from requests import RequestException


class BaseChatService:
    """Wraps interactions with the chat completion API."""

    def __init__(
        self,
        api_key: str,
        api_base: str,
        persona_path: str | Path,
        user_id: Optional[str] = None,
        app_title: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: int = 30,
        fallback_persona: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._api_base = api_base.rstrip("/")
        self._endpoint = f"{self._api_base}/chat/completions"
        self._user_id = user_id
        self._app_title = app_title
        self._model = model
        self._timeout = timeout
        self._persona_path = Path(persona_path)
        self._fallback_persona = fallback_persona
        self._persona = self._load_persona()

    def _load_persona(self) -> str:
        if self._persona_path.exists():
            return self._persona_path.read_text(encoding="utf-8").strip()
        if self._fallback_persona:
            return self._fallback_persona.strip()
        return "回覆時請用繁體中文。"

    def _headers(self) -> dict:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if self._user_id:
            headers["X-User-Id"] = self._user_id
        if self._app_title:
            headers["X-Title"] = self._app_title
        return headers

    def _build_messages(self, user_text: str) -> List[dict]:
        return [
            {"role": "system", "content": self._persona},
            {
                "role": "user",
                "content": user_text,
            },
        ]

    async def generate_reply(self, user_text: str) -> str:
        """Call the chat completion API in a worker thread."""

        def _call() -> str:
            payload = {
                "model": self._model,
                "messages": self._build_messages(user_text),
                "temperature": 0.85,
                "max_tokens": 300,
            }
            response = requests.post(
                self._endpoint,
                headers=self._headers(),
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        try:
            return await asyncio.to_thread(_call)
        except RequestException:
            return "Cony 暫時連不上粉紅雲端，先跟你抱歉！稍後再試一次好嗎？"
        except Exception:
            return "Cony 今天有點累，等我補妝一下再回你～"
