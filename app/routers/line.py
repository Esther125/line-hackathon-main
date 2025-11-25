"""LINE webhook router."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from app.config import Settings, get_settings
from app.dependencies import get_line_chat_service
from app.services.line_chat_service import LineChatService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["line-webhook"])


@router.post("/callback")
async def line_callback(
    request: Request,
    x_line_signature: str = Header(..., alias="x-line-signature"),
    settings: Settings = Depends(get_settings),
    chat_service: LineChatService = Depends(get_line_chat_service),
) -> dict:
    """Receive LINE webhook events and reply using the Cony chat persona."""

    body = await request.body()
    parser = WebhookParser(settings.line_channel_secret)
    line_bot_api = LineBotApi(settings.line_channel_access_token)

    try:
        events = parser.parse(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError as exc:  # pragma: no cover - defensive
        logger.warning("Invalid LINE signature: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_text = event.message.text or ""
            reply_text = await chat_service.generate_reply(user_text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text),
            )

    return {"received_events": len(events)}
