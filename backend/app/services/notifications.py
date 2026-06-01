from dataclasses import dataclass
from enum import StrEnum


class NotificationType(StrEnum):
    NEW_ITEM = "new_item"
    PRICE_DROP = "price_drop"
    HIGH_PROFIT = "high_profit"


@dataclass(frozen=True)
class NotificationDraft:
    user_id: int
    item_id: int
    type: NotificationType
    message: str


class NotificationPlanner:
    """Placeholder for future automatic notifications."""

    def plan_for_new_item(self, user_id: int, item_id: int, profit: int) -> list[NotificationDraft]:
        if profit <= 0:
            return []
        return [
            NotificationDraft(
                user_id=user_id,
                item_id=item_id,
                type=NotificationType.HIGH_PROFIT,
                message="Найден товар с высокой потенциальной прибылью.",
            )
        ]
