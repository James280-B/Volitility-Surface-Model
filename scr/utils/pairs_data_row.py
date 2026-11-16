from typing import Protocol

class PairsDataRow(Protocol):
    index: int
    strike: float
    underlying_price_call: float
    underlying_price_put: float
    price_put: float
    price_call: float

