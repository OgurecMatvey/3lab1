
from dataclasses import dataclass, field
from datetime import date
from typing import Dict


@dataclass(frozen=True)
class CurrencyRate:

    day: date
    rates: Dict[str, float] = field(default_factory=dict)

    def rate_for(self, currency: str) -> float:
        if currency not in self.rates:
            raise KeyError(f"Нет данных по валюте {currency} за {self.day}")
        return self.rates[currency]


@dataclass(frozen=True)
class ChangeEvent:

    day: date
    value: float
