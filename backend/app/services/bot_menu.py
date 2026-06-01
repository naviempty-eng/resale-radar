from typing import Any

from app.core.config import get_settings


def main_menu() -> dict[str, Any]:
    settings = get_settings()
    app_button: dict[str, Any]
    if settings.mini_app_url.startswith("https://"):
        app_button = {
            "text": "Открыть приложение",
            "web_app": {"url": settings.mini_app_url},
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
