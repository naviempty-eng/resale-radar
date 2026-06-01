from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User


DbSession = Annotated[Session, Depends(get_db)]


def get_or_create_user(
    db: DbSession,
    x_telegram_id: Annotated[int | None, Header(alias="X-Telegram-Id")] = None,
    x_telegram_username: Annotated[str | None, Header(alias="X-Telegram-Username")] = None,
) -> User:
    settings = get_settings()
    telegram_id = x_telegram_id or settings.dev_default_telegram_id
    user = db.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(telegram_id=telegram_id, username=x_telegram_username)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif x_telegram_username and user.username != x_telegram_username:
        user.username = x_telegram_username
        db.commit()
        db.refresh(user)
    return user


CurrentUser = Annotated[User, Depends(get_or_create_user)]
