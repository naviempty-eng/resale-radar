from pydantic import BaseModel


class ItemRead(BaseModel):
    id: int
    title: str
    brand: str
    country: str
    platform: str
    category: str
    size: str
    image_url: str
    purchase_price: int
    shipping_price: int
    total_price_rub: int
    avito_price: int
    expected_profit: int
    risk_level: str
    seller_is_suspicious: bool
    authenticity_risk: str
    source_url: str

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    items: list[ItemRead]
