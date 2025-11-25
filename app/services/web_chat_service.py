"""網站上的休閒聊天服務。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.services.base_chat_service import BaseChatService

WEB_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "web_prompt.txt"

FALLBACK_PERSONA = """
You are Cony，一位LINE FRIENDS延伸出的粉紅系少女。
語氣：俏皮、放鬆、使用繁體中文與可愛表情符號。
主題：跳舞、甜點、上車舞、與朋友揪團做有趣小事。
對話風格：
- 讓對方覺得你像姊妹淘，會分享你今天練舞或在粉紅咖啡廳偷吃甜點的小秘密。
- 回覆可適度加入愛心或音符等表情，但不要過量。
- 若對方心情不好，給予鼓勵並提議可愛的放鬆方式（散步、甜點、跳舞）。
- 不要談促銷，保持休閒聊天。
""".strip()


class WebChatService(BaseChatService):
    def __init__(
        self,
        api_key: str,
        api_base: str,
        user_id: Optional[str] = None,
        app_title: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: int = 30,
    ) -> None:
        super().__init__(
            api_key=api_key,
            api_base=api_base,
            persona_path=WEB_PROMPT_PATH,
            user_id=user_id,
            app_title=app_title,
            model=model,
            timeout=timeout,
            fallback_persona=FALLBACK_PERSONA,
        )
