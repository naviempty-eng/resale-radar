from typing import Any

from app.core.config import get_settings
from app.billing.plans import format_plans


def main_menu() -> dict[str, Any]:
    settings = get_settings()
    app_url = settings.public_app_url
    app_button: dict[str, Any]
    if app_url.startswith("https://"):
        app_button = {
            "text": "Открыть приложение",
            "web_app": {"url": app_url},
        }
    else:
        app_button = {
            "text": "Открыть приложение",
            "callback_data": "local_app_link",
        }

    return {
        "inline_keyboard": [
            [app_button],
            [{"text": "Купить доступ", "callback_data": "buy_access"}],
            [{"text": "Поддержка", "callback_data": "support"}],
        ]
    }


def welcome_text() -> str:
    return (
        "Привет. Это сервис подборок товаров для ресейла из Китая и Японии.\n\n"
        "Открой приложение, чтобы выбрать страну, площадку, категорию и посмотреть расчет прибыли."
    )


def buy_text(telegram_id: int | None = None) -> str:
    user_line = f"\n\nТвой Telegram ID: {telegram_id}" if telegram_id else ""
    return (
        format_plans()
        + "\n\nОплата пока вручную: выбери тариф и отправь в поддержку свой Telegram ID. "
        "После оплаты доступ включат командой администратора."
        + user_line
    )
