"""
Статистическое прогнозирование методом экстраполяции по скользящей средней.

Прогноз на день (t+1) = среднее последних n фактических/спрогнозированных
значений. Прогнозные значения затем сами участвуют в расчёте следующих
точек (см. пример в методичке).

Применённые принципы:
- Абстракция: Forecaster задаёт контракт "forecast(values, n, horizon)"
- Полиморфизм: можно добавить, например, ExponentialSmoothingForecaster,
  не трогая остальной код (frontend работает с типом Forecaster).

Автор: backend (участник 1)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class Forecaster(ABC):
    @abstractmethod
    def forecast(self, values: List[float], n: int, horizon: int) -> List[float]:
        """Вернуть horizon спрогнозированных значений на основе values."""
        raise NotImplementedError


class MovingAverageForecaster(Forecaster):
    """Экстраполяция по скользящей средней с окном n."""

    def forecast(self, values: List[float], n: int, horizon: int) -> List[float]:
        if n < 1:
            raise ValueError("Период скользящей средней n должен быть >= 1")
        if n > len(values):
            raise ValueError(
                f"Недостаточно данных: n={n}, а фактических точек только {len(values)}"
            )
        if horizon < 1:
            raise ValueError("Горизонт прогноза должен быть >= 1")

        series = list(values)
        forecasted: List[float] = []

        for _ in range(horizon):
            window = series[-n:]
            next_value = sum(window) / n
            series.append(next_value)
            forecasted.append(next_value)

        return forecasted
