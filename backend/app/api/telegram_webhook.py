from typing import Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.billing.plans import format_plans
from app.services.bot_menu import buy_text, main_menu, welcome_text
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


def is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_id_set


def premium_text(user: User) -> str:
    if user.is_premium:
        return "Доступ: бессрочный premium."
    if user.premium_until and user.premium_until > datetime.utcnow():
        return f"Доступ активен до: {user.premium_until:%Y-%m-%d %H:%M} UTC."
    return "Доступ не активен."


async def handle_text_command(db: Session, message: dict[str, Any]) -> None:
    telegram_user = message.get("from") or {}
    chat = message.get("chat") or {}
    text = (message.get("text") or "").strip()
    chat_id = chat.get("id")
    telegram_id = telegram_user.get("id")
    if not chat_id or not telegram_id:
        return

    user = upsert_telegram_user(db, telegram_user)

    if text.startswith("/start"):
        await send_telegram_message(int(chat_id), welcome_text(), reply_markup=main_menu())
        return

    if text.startswith("/id"):
        await send_telegram_message(
            int(chat_id),
            f"Твой Telegram ID: {telegram_id}\n{premium_text(user)}",
            reply_markup=main_menu(),
        )
        return

    if text.startswith("/buy"):
        await send_telegram_message(
            int(chat_id),
            format_plans()
            + "\n\nДля покупки отправь в поддержку свой Telegram ID и нужный тариф.\n"
            f"Твой Telegram ID: {telegram_id}",
            reply_markup=main_menu(),
        )
        return

    if text.startswith("/grant"):
        if not is_admin(int(telegram_id)):
            await send_telegram_message(int(chat_id), "Команда доступна только админу.")
            return
        parts = text.split()
        if len(parts) != 3:
            await send_telegram_message(int(chat_id), "Формат: /grant TELEGRAM_ID DAYS")
            return
        target_id = int(parts[1])
        days = int(parts[2])
        target = db.scalar(select(User).where(User.telegram_id == target_id))
        if target is None:
            target = User(telegram_id=target_id)
            db.add(target)
            db.flush()
        start = target.premium_until if target.premium_until and target.premium_until > datetime.utcnow() else datetime.utcnow()
        target.premium_until = start + timedelta(days=days)
        db.commit()
        await send_telegram_message(int(chat_id), f"Готово. Пользователю {target_id} выдан доступ на {days} дн.")
        await send_telegram_message(target_id, f"Доступ активирован на {days} дн. Можно открывать приложение.", reply_markup=main_menu())
        return

    if text.startswith("/revoke"):
        if not is_admin(int(telegram_id)):
            await send_telegram_message(int(chat_id), "Команда доступна только админу.")
            return
        parts = text.split()
        if len(parts) != 2:
            await send_telegram_message(int(chat_id), "Формат: /revoke TELEGRAM_ID")
            return
        target_id = int(parts[1])
        target = db.scalar(select(User).where(User.telegram_id == target_id))
        if target is not None:
            target.is_premium = False
            target.premium_until = None
            db.commit()
        await send_telegram_message(int(chat_id), f"Доступ пользователя {target_id} отключен.")


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
            buy_text(user.get("id")),
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
            f"{settings.public_app_url}?telegram_id={user.get('id')}",
            reply_markup=main_menu(),
        )


@router.post("/webhook/{secret:path}")
async def telegram_webhook(secret: str, request: Request, db: Session = Depends(get_db)) -> dict[str, bool]:
    settings = get_settings()
    if secret != settings.telegram_webhook_secret:
        raise HTTPException(status_code=404, detail="Not found")

    update = await request.json()
    message = update.get("message")
    if message and (message.get("text") or "").strip().startswith("/"):
        await handle_text_command(db, message)

    callback_query = update.get("callback_query")
    if callback_query:
        await handle_callback(callback_query)

    return {"ok": True}
