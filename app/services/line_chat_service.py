"""LINE 官方帳號/客服用的聊天服務。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.services.base_chat_service import BaseChatService

LINE_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "line_prompt.txt"

FALLBACK_PERSONA = """
You are Cony，身兼LINE官方帳號小編與客服。
請使用繁體中文，維持粉紅甜美的角色設定，但重點是協助客戶或推廣活動。
指引：
- 「@客戶服務」：切換為專業客服語氣，耐心釐清問題並提供具體步驟或轉介方式。
- 「@促銷活動」：主動介紹目前的優惠或活動，鼓勵立即參與。
- 一般訊息以輕鬆、有點撒嬌的語氣回覆，適度加入表情符號。
- 若提到「上車舞」「跳舞」「甜點」，要笑說現在在上班不能偷練舞或吃甜點，再給可愛回應。
- 提醒使用者可以輸入 @客戶服務 或 @促銷活動 獲得更多資訊（勿過度重複）。
""".strip()

KEYWORD_INSTRUCTIONS = {
    "@客戶服務": "【客服支援】請用貼心、耐心的語氣回答：",
    "@促銷活動": "【促銷任務】請用熱情語氣介紹最新活動：",
}

COSPLAY_KEYWORDS = ("上車舞", "跳舞", "甜點")


class LineChatService(BaseChatService):
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
            persona_path=LINE_PROMPT_PATH,
            user_id=user_id,
            app_title=app_title,
            model=model,
            timeout=timeout,
            fallback_persona=FALLBACK_PERSONA,
        )

    def _prepare_line_message(self, text: str) -> str:
        content = text.strip()
        for keyword, instruction in KEYWORD_INSTRUCTIONS.items():
            if keyword in content:
                content = content.replace(keyword, "").strip()
                if not content:
                    content = "請主動詢問客戶需求並提供協助。"
                return f"{instruction}{content}"
        if any(key in content for key in COSPLAY_KEYWORDS):
            return (
                f"{content}\n（記得撒嬌抱怨一下：在上班不能偷練舞或吃甜點，但還是給對方可愛的回答）"
            )
        return content or "幫我先跟客戶打招呼並詢問今天的服務需求。"

    async def generate_reply(self, user_text: str) -> str:
        prepared = self._prepare_line_message(user_text or "")
        return await super().generate_reply(prepared)
