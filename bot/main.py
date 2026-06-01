import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from config import get_settings

settings = get_settings()
dp = Dispatcher()
logger = logging.getLogger(__name__)


def main_menu() -> InlineKeyboardMarkup:
    app_button = (
        InlineKeyboardButton(
            text="Открыть приложение",
            web_app=WebAppInfo(url=settings.mini_app_url),
        )
        if settings.mini_app_url.startswith("https://")
        else InlineKeyboardButton(
            text="Открыть приложение",
            callback_data="local_app_link",
        )
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [app_button],
            [InlineKeyboardButton(text="Купить доступ", callback_data="buy_access")],
            [InlineKeyboardButton(text="Поддержка", callback_data="support")],
        ]
    )


async def register_user(message: Message) -> None:
    payload = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(f"{settings.backend_url}/api/users", json=payload)
    except httpx.HTTPError as exc:
        logger.warning("Backend user registration failed: %s", exc)


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await register_user(message)
    await message.answer(
        "Привет. Это сервис подборок товаров для ресейла из Китая и Японии.\n\n"
        "Открой приложение, чтобы выбрать страну, площадку, категорию и посмотреть расчет прибыли.",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "buy_access")
async def buy_access(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Оплата пока не подключена.\n\n"
        "В MVP доступ управляется флагом is_premium. Для теста открой приложение и нажми "
        "\"Активировать демо-доступ\" на экране оплаты-заглушки.",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "local_app_link")
async def local_app_link(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Telegram не открывает локальный localhost как Mini App.\n\n"
        "Для теста открой приложение в браузере на Mac:\n"
        f"{settings.mini_app_url}?telegram_id={callback.from_user.id}",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery) -> None:
    await callback.message.answer(
        f"Поддержка: @{settings.support_username}\n\n"
        "Можно написать по вопросам доступа, выкупа товара, посредников и ошибок в подборках.",
        reply_markup=main_menu(),
    )
    await callback.answer()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
