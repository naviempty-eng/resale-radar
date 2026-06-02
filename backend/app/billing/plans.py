from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    code: str
    title: str
    days: int
    price_rub: int
    note: str


PLANS: tuple[Plan, ...] = (
    Plan(code="day", title="Пробный день", days=1, price_rub=99, note="Понять механику и посмотреть подборки."),
    Plan(code="week", title="Неделя", days=7, price_rub=399, note="Нормально протестировать спрос и категории."),
    Plan(code="month", title="Месяц", days=30, price_rub=990, note="Базовый тариф для регулярного ресейла."),
    Plan(code="year", title="Год", days=365, price_rub=7990, note="Самая выгодная цена за месяц."),
)


def format_plans() -> str:
    lines = ["Тарифы доступа:"]
    for plan in PLANS:
        lines.append(f"- {plan.title}: {plan.price_rub} ₽ / {plan.days} дн.")
    return "\n".join(lines)
