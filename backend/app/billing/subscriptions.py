from app.models.user import User


class SubscriptionService:
    def has_access(self, user: User) -> bool:
        return user.is_premium

    def activate_manual_access(self, user: User) -> None:
        user.is_premium = True
