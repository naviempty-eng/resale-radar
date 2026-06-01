from dataclasses import dataclass


@dataclass(frozen=True)
class AvitoPriceEstimate:
    average_price_rub: int
    sample_size: int
    confidence: str


class AvitoPriceAnalyzer:
    async def estimate(self, title: str, brand: str, size: str) -> AvitoPriceEstimate:
        raise NotImplementedError("Avito price analysis will be connected later.")
