from typing import Annotated

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.favorite import Favorite
from app.models.instruction import Instruction
from app.models.item import Item
from app.models.user import User
from app.schemas.instruction import InstructionResponse
from app.schemas.item import ItemListResponse, ItemRead
from app.schemas.user import UserCreate, UserRead
from app.services.instructions import build_instruction
from app.services.telegram import send_telegram_message

router = APIRouter(prefix="/api")


def require_premium(user: User) -> None:
    if not user.access_active:
        raise HTTPException(status_code=402, detail="Premium access is required")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/users", response_model=UserRead)
def upsert_user(payload: UserCreate, db: DbSession) -> User:
    user = db.scalar(select(User).where(User.telegram_id == payload.telegram_id))
    if user is None:
        user = User(telegram_id=payload.telegram_id, username=payload.username)
        db.add(user)
    else:
        user.username = payload.username
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/me", response_model=UserRead)
def read_me(user: CurrentUser) -> User:
    return user


@router.post("/users/me/payment-request", response_model=UserRead)
def create_payment_request(user: CurrentUser, db: DbSession) -> User:
    db.commit()
    db.refresh(user)
    return user


@router.get("/items", response_model=ItemListResponse)
def list_items(
    user: CurrentUser,
    db: DbSession,
    country: Annotated[str | None, Query()] = None,
    platform: Annotated[str | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
) -> ItemListResponse:
    require_premium(user)
    query = select(Item).where(Item.seller_is_suspicious.is_(False)).order_by(Item.expected_profit.desc())
    if country:
        query = query.where(Item.country == country)
    if platform:
        query = query.where(Item.platform == platform)
    if category:
        query = query.where(Item.category == category)
    items = db.scalars(query).all()
    return ItemListResponse(items=list(items))


@router.get("/items/{item_id}", response_model=ItemRead)
def read_item(item_id: int, user: CurrentUser, db: DbSession) -> Item:
    require_premium(user)
    item = db.scalar(select(Item).where(Item.id == item_id, Item.seller_is_suspicious.is_(False)))
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items/{item_id}/instruction", response_model=InstructionResponse)
async def request_instruction(item_id: int, user: CurrentUser, db: DbSession) -> InstructionResponse:
    require_premium(user)
    item = db.scalar(
        select(Item)
        .options(selectinload(Item.instruction))
        .where(Item.id == item_id, Item.seller_is_suspicious.is_(False))
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    instruction = item.instruction
    if instruction is None:
        instruction = Instruction(item_id=item.id, content=build_instruction(item))
        db.add(instruction)
        db.commit()
        db.refresh(instruction)

    sent = await send_telegram_message(user.telegram_id, instruction.content)
    return InstructionResponse(sent=sent, content=instruction.content)


@router.get("/favorites", response_model=ItemListResponse)
def list_favorites(user: CurrentUser, db: DbSession) -> ItemListResponse:
    require_premium(user)
    items = db.scalars(
        select(Item)
        .join(Favorite)
        .where(Favorite.user_id == user.id, Item.seller_is_suspicious.is_(False))
        .order_by(Item.expected_profit.desc())
    ).all()
    return ItemListResponse(items=list(items))


@router.post("/favorites/{item_id}", response_model=ItemRead)
def add_favorite(item_id: int, user: CurrentUser, db: DbSession) -> Item:
    require_premium(user)
    item = db.scalar(select(Item).where(Item.id == item_id, Item.seller_is_suspicious.is_(False)))
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    exists = db.scalar(select(Favorite).where(Favorite.user_id == user.id, Favorite.item_id == item.id))
    if exists is None:
        db.add(Favorite(user_id=user.id, item_id=item.id))
        db.commit()
    return item


@router.delete("/favorites/{item_id}")
def remove_favorite(item_id: int, user: CurrentUser, db: DbSession) -> dict[str, bool]:
    favorite = db.scalar(select(Favorite).where(Favorite.user_id == user.id, Favorite.item_id == item_id))
    if favorite is not None:
        db.delete(favorite)
        db.commit()
    return {"ok": True}
