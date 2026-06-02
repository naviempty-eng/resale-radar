from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None


class UserRead(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    is_premium: bool
    premium_until: datetime | None
    access_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
