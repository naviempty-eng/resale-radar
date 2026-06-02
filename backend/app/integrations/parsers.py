from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExternalItem:
    title: str
    brand: str
    country: str
    platform: str
    category: str
    size: str
    image_url: str
    purchase_price_native: int
    source_url: str
    seller_id: str | None = None


class MarketplaceParser(Protocol):
    async def search(self, query: str, category: str) -> list[ExternalItem]:
        raise NotImplementedError


class GoofishParser:
    async def search(self, query: str, category: str) -> list[ExternalItem]:
        raise NotImplementedError("Goofish parser will be connected later.")


class MercariParser:
    async def search(self, query: str, category: str) -> list[ExternalItem]:
        raise NotImplementedError("Mercari parser will be connected later.")


class YahooAuctionsParser:
    async def search(self, query: str, category: str) -> list[ExternalItem]:
        raise NotImplementedError("Yahoo Auctions parser will be connected later.")


class EbayParser:
    async def search(self, query: str, category: str) -> list[ExternalItem]:
        raise NotImplementedError("eBay parser will be connected later.")


class DepopParser:
    async def search(self, query: str, category: str) -> list[ExternalItem]:
        raise NotImplementedError("Depop parser will be connected later.")


class MercariUsParser:
    async def search(self, query: str, category: str) -> list[ExternalItem]:
        raise NotImplementedError("Mercari US parser will be connected later.")
