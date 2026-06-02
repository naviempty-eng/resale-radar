from app.models.item import Item


def get_logistics(item: Item) -> dict[str, str]:
    if item.country == "Китай":
        return {
            "manager": "@BogeManager",
            "price": "260 руб/кг без комиссии",
            "timing": "20-25 дней",
        }
    if item.country == "США":
        return {
            "manager": "@IneartheDManager",
            "price": "1500 руб/кг + комиссия 1500 руб",
            "timing": "12-20 дней",
        }
    return {
        "manager": "@IneartheDManager",
        "price": "1400 руб/кг + 4% от стоимости товара",
        "timing": "5-10 дней",
    }


def authenticity_percent(risk: str) -> int:
    if risk == "high":
        return 58
    if risk == "medium":
        return 76
    return 92


def build_instruction(item: Item) -> str:
    logistics = get_logistics(item)
    message_to_manager = f"Привет, хочу заказать: {item.platform}\n{item.title}\n{item.source_url}"

    return (
        f"Инструкция по товару: {item.title}\n\n"
        f"Посредник: {logistics['manager']}\n\n"
        "Текст для копирования посреднику:\n"
        f"{message_to_manager}\n\n"
        "Как выкупить товар:\n"
        "1. Открой ссылку на товар и проверь актуальность цены, размер и состояние.\n"
        f"2. Напиши {logistics['manager']} и отправь текст выше.\n"
        "3. Попроси финальный расчет до оплаты: товар, доставка по стране, международная доставка, комиссия и срок.\n"
        "4. Не оплачивай напрямую продавцу, работай через посредника.\n\n"
        "Примерный расчет логистики:\n"
        f"{item.country}: {logistics['price']}.\n"
        f"Сроки: {logistics['timing']}.\n\n"
        "Что проверить перед покупкой:\n"
        "- рейтинг и историю продавца;\n"
        "- реальные фото товара;\n"
        "- бирки, швы, подошву, фурнитуру, серийники;\n"
        "- дефекты, комплект и коробку;\n"
        f"- оригинальность по оценке сервиса: {authenticity_percent(item.authenticity_risk)}%.\n\n"
        "Как продавать товар:\n"
        "Ставь цену немного выше средней по Авито, оставь пространство для торга и поднимай объявление в первые дни.\n\n"
        "Где размещать объявление:\n"
        "Авито, Юла, Telegram-ресейл чаты, VK-группы по бренду и локальные городские барахолки.\n\n"
        "Как фотографировать товар:\n"
        "Снимай при дневном свете: общий вид, бок, бирки, размер, подошву/фурнитуру, дефекты и комплект.\n\n"
        "Пример описания для Авито:\n"
        f"{item.brand} {item.title}, размер {item.size}. Состояние отличное, привезено из {item.country}. "
        "Есть подробные фото, отправлю видео по запросу. Возможна встреча или доставка."
    )
