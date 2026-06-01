from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.bot_menu import main_menu, welcome_text
from app.services.telegram import answer_callback_query, send_telegram_message

router = APIRouter(prefix="/api/telegram")


def upsert_telegram_user(db: Session, telegram_user: dict[str, Any]) -> User:
    telegram_id = int(telegram_user["id"])
    username = telegram_user.get("username")
    user = db.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
    else:
        user.username = username
    db.commit()
    db.refresh(user)
    return user


async def handle_start(db: Session, message: dict[str, Any]) -> None:
    telegram_user = message.get("from") or {}
    chat = message.get("chat") or {}
    if not telegram_user.get("id") or not chat.get("id"):
        return
    upsert_telegram_user(db, telegram_user)
    await send_telegram_message(int(chat["id"]), welcome_text(), reply_markup=main_menu())


async def handle_callback(callback_query: dict[str, Any]) -> None:
    settings = get_settings()
    callback_id = callback_query.get("id")
    data = callback_query.get("data")
    message = callback_query.get("message") or {}
    chat = message.get("chat") or {}
    user = callback_query.get("from") or {}
    chat_id = chat.get("id")

    if callback_id:
        await answer_callback_query(callback_id)
    if not chat_id:
        return

    if data == "buy_access":
        await send_telegram_message(
            int(chat_id),
            "Оплата пока не подключена.\n\n"
            "В MVP доступ управляется флагом is_premium. Для теста открой приложение и нажми "
            "\"Активировать демо-доступ\" на экране оплаты-заглушки.",
            reply_markup=main_menu(),
        )
    elif data == "support":
        await send_telegram_message(
            int(chat_id),
            f"Поддержка: @{settings.support_username}\n\n"
            "Можно написать по вопросам доступа, выкупа товара, посредников и ошибок в подборках.",
            reply_markup=main_menu(),
        )
    elif data == "local_app_link":
        await send_telegram_message(
            int(chat_id),
            "Telegram не открывает локальный localhost как Mini App.\n\n"
            "Для теста открой приложение в браузере на Mac:\n"
            f"{settings.mini_app_url}?telegram_id={user.get('id')}",
            reply_markup=main_menu(),
        )


@router.post("/webhook/{secret}")
async def telegram_webhook(secret: str, request: Request, db: Session = Depends(get_db)) -> dict[str, bool]:
    settings = get_settings()
    if secret != settings.telegram_webhook_secret:
        raise HTTPException(status_code=404, detail="Not found")

    update = await request.json()
    message = update.get("message")
    if message and (message.get("text") or "").strip().startswith("/start"):
        await handle_start(db, message)

    callback_query = update.get("callback_query")
    if callback_query:
        await handle_callback(callback_query)

    return {"ok": True}
