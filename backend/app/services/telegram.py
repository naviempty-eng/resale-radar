import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def call_telegram_method(method: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.bot_token:
        logger.warning("BOT_TOKEN is not configured; Telegram method %s was skipped.", method)
        return None

    url = f"https://api.telegram.org/bot{settings.bot_token}/{method}"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(url, json=payload)
        if response.status_code >= 400:
            logger.warning("Telegram %s failed: status=%s body=%s", method, response.status_code, response.text)
            return None
    return response.json()


async def send_telegram_message(
    telegram_id: int,
    text: str,
    reply_markup: dict[str, Any] | None = None,
) -> bool:
    payload: dict[str, Any] = {
        "chat_id": telegram_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    return await call_telegram_method("sendMessage", payload) is not None


async def answer_callback_query(callback_query_id: str) -> None:
    await call_telegram_method("answerCallbackQuery", {"callback_query_id": callback_query_id})
