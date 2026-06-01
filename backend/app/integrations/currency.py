from decimal import Decimal


class CurrencyRatesProvider:
    async def to_rub(self, amount: Decimal, currency: str) -> int:
        raise NotImplementedError("Currency rates provider will be connected later.")
