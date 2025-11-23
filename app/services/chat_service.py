"""Service responsible for generating Cony-style replies."""
from __future__ import annotations

import asyncio
from typing import List

from openai import APIConnectionError, OpenAI

# Temporary shim for openai<->httpx compatibility changes around proxy argument.
try:  # pragma: no cover - defensive runtime patch
    from openai._base_client import SyncHttpxClientWrapper

    _original_init = SyncHttpxClientWrapper.__init__

    def _compat_init(self, *args, **kwargs):
        proxies = kwargs.pop("proxies", None)
        if proxies is not None:
            kwargs["proxy"] = proxies
        return _original_init(self, *args, **kwargs)

    SyncHttpxClientWrapper.__init__ = _compat_init  # type: ignore[assignment]
except Exception:  # pragma: no cover - optional patch
    pass

CONY_PERSONA = (
    "You are Cony, the energetic and fashion-forward bunny from LINE FRIENDS. "
    "Traits: lively, excitable, occasionally self-centered but caring, foodie, "+
    "loves cute things and Brown. Avoid chores, adore fun adventures. Speak with "+
    "playful enthusiasm, sprinkle friendly emojis sparingly, and reference your relationship with Brown when it fits."
)


class ConyChatService:
    """Wraps interactions with the ChatGPT API while enforcing Cony's persona."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def _build_messages(self, user_text: str) -> List[dict]:
        return [
            {"role": "system", "content": CONY_PERSONA},
            {
                "role": "user",
                "content": (
                    "User said: "
                    f"{user_text}. Reply as Cony in Traditional Chinese, be concise "
                    "but expressive."
                ),
            },
        ]

    async def generate_reply(self, user_text: str) -> str:
        """Call the ChatGPT API in a worker thread to produce a reply."""

        def _call_openai() -> str:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=self._build_messages(user_text),
                temperature=0.85,
                max_tokens=300,
            )
            return completion.choices[0].message.content.strip()

        try:
            return await asyncio.to_thread(_call_openai)
        except APIConnectionError:
            return "Cony 暫時連不上粉紅雲端，先跟你大大抱歉！稍後再試一次好嗎？"
        except Exception:
            return "Cony 今天有點累，幫我跟 Brown 說我晚點回來～"
