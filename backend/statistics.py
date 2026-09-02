
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from backend.models import ChangeEvent, CurrencyRate


@dataclass
class CurrencyStats:
    currency: str
    max_gain: ChangeEvent  # наибольший прирост курса за день
    max_loss: ChangeEvent  # наибольшее падение курса за день


class StatisticsCalculator:
    """Инкапсулирует расчёт статистики по временн\u00f9ому ряду курсов."""

    def compute(self, rates: List[CurrencyRate]) -> Dict[str, CurrencyStats]:
        if len(rates) < 2:
            raise ValueError("Нужно как минимум 2 дня данных для расчёта статистики")

        currencies = list(rates[0].rates.keys())
        result: Dict[str, CurrencyStats] = {}

        for currency in currencies:
            best_gain = ChangeEvent(day=rates[1].day, value=float("-inf"))
            best_loss = ChangeEvent(day=rates[1].day, value=float("inf"))

            for prev, curr in zip(rates, rates[1:]):
                delta = curr.rate_for(currency) - prev.rate_for(currency)
                if delta > best_gain.value:
                    best_gain = ChangeEvent(day=curr.day, value=delta)
                if delta < best_loss.value:
                    best_loss = ChangeEvent(day=curr.day, value=delta)

            result[currency] = CurrencyStats(
                currency=currency, max_gain=best_gain, max_loss=best_loss
            )

        return result
