"""Service responsible for generating Cony-style replies."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List, Optional

import requests
from requests import RequestException

DEFAULT_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "prompt.txt"


class ConyChatService:
    """Wraps interactions with the ChatGPT API while enforcing Cony's persona."""

    def __init__(
        self,
        api_key: str,
        api_base: str,
        user_id: Optional[str] = None,
        app_title: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: int = 30,
    ) -> None:
        self._api_key = api_key
        self._api_base = api_base.rstrip("/")
        self._endpoint = f"{self._api_base}/chat/completions"
        self._user_id = user_id
        self._app_title = app_title
        self._model = model
        self._timeout = timeout
        self._persona = self._load_persona()

    def _build_messages(self, user_text: str) -> List[dict]:
        return [
            {"role": "system", "content": self._persona},
            {
                "role": "user",
                "content": (
                    "User said: "
                    f"{user_text}. Reply as Cony in Traditional Chinese, be concise "
                    "but expressive."
                ),
            },
        ]

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

    async def generate_reply(self, user_text: str) -> str:
        """Call the ChatGPT API in a worker thread to produce a reply."""

        def _call_proxy() -> str:
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
            return await asyncio.to_thread(_call_proxy)
        except RequestException:
            return "Cony 暫時連不上粉紅雲端，先跟你大大抱歉！稍後再試一次好嗎？"
        except Exception:
            return "Cony 今天有點累，幫我跟 Brown 說我晚點回來～"
    def _load_persona(self) -> str:
        if DEFAULT_PROMPT_PATH.exists():
            return DEFAULT_PROMPT_PATH.read_text(encoding="utf-8").strip()
        return (
            "You are Cony,一位 LINE FRIENDS 延伸出來的兔子系少女，熱愛粉紅色、甜點、舞台與可愛表演。"
            " 你剛解鎖熱門的「上車舞」，永遠戴著白色兔子髮箍，說話活潑又撒嬌。"
            " Personality: energetic, affectionate, bubbly, instantly befriending everyone."
            " Tone: 可愛、熱情、表情符號很多但易讀。"
            " 經常提到跳舞練習、甜點，以及粉紅穿搭。"
        )
