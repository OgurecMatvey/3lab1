
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import filedialog, ttk
from typing import Dict, List, Optional

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (  # noqa: E402
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.figure import Figure  # noqa: E402


class ChartWidget(ttk.Frame):
    """Обёртка над matplotlib Figure, встроенная в Tkinter.

    Панель инструментов matplotlib (NavigationToolbar2Tk) уже даёт
    масштабирование (лупа) и панорамирование графика "из коробки".
    Дополнительно есть выбор периода (последние N дней) и кнопка экспорта.
    """

    def __init__(self, master: tk.Widget):
        super().__init__(master)

        self._dates: List[date] = []
        self._series: Dict[str, List[float]] = {}
        self._forecast_dates: List[date] = []
        self._forecast_series: Dict[str, List[float]] = {}

        controls = ttk.Frame(self)
        controls.pack(side="top", fill="x")

        ttk.Label(controls, text="Период:").pack(side="left", padx=(4, 2))
        self.period_var = tk.StringVar(value="Весь период")
        self.period_box = ttk.Combobox(
            controls,
            textvariable=self.period_var,
            state="readonly",
            width=16,
            values=["Весь период", "Последние 7 дней", "Последние 14 дней"],
        )
        self.period_box.pack(side="left")
        self.period_box.bind("<<ComboboxSelected>>", lambda _e: self.redraw())

        ttk.Button(controls, text="Экспорт графика...", command=self.export).pack(
            side="right", padx=4
        )

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Панель инструментов даёт zoom / pan / сохранение "из коробки".
        self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side="bottom", fill="x")

    def set_data(
        self,
        dates: List[date],
        series: Dict[str, List[float]],
        forecast_dates: Optional[List[date]] = None,
        forecast_series: Optional[Dict[str, List[float]]] = None,
    ) -> None:
        self._dates = dates
        self._series = series
        self._forecast_dates = forecast_dates or []
        self._forecast_series = forecast_series or {}
        self.redraw()

    def redraw(self) -> None:
        self.ax.clear()
        dates, series = self._apply_period_filter()

        color_cycle = ["#1f77b4", "#2ca02c", "#9467bd", "#8c564b"]
        for i, (currency, values) in enumerate(series.items()):
            color = color_cycle[i % len(color_cycle)]
            self.ax.plot(dates, values, label=currency, color=color, marker="o", markersize=3)

            forecast_values = self._forecast_series.get(currency)
            if forecast_values and self._forecast_dates:
                # Прогноз рисуется другим (пунктирным, более светлым) цветом,
                # начиная с последней фактической точки, чтобы линия была непрерывной.
                join_dates = [dates[-1]] + self._forecast_dates if dates else self._forecast_dates
                join_values = [values[-1]] + forecast_values if values else forecast_values
                self.ax.plot(
                    join_dates,
                    join_values,
                    label=f"{currency} (прогноз)",
                    color=color,
                    linestyle="--",
                    alpha=0.55,
                    marker="x",
                    markersize=4,
                )

        self.ax.set_xlabel("День")
        self.ax.set_ylabel("Курс, ₽")
        self.ax.set_title("Курс рубля к валютам")
        if series:
            self.ax.legend(loc="best", fontsize=8)
        self.ax.grid(True, alpha=0.3)
        self.figure.autofmt_xdate(rotation=45)
        self.canvas.draw_idle()

    def _apply_period_filter(self):
        choice = self.period_var.get()
        if choice == "Последние 7 дней":
            n = 7
        elif choice == "Последние 14 дней":
            n = 14
        else:
            n = None

        if not n or n >= len(self._dates):
            return self._dates, self._series

        dates = self._dates[-n:]
        series = {cur: vals[-n:] for cur, vals in self._series.items()}
        return dates, series

    def export(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Экспорт графика",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("PDF", "*.pdf"),
                ("SVG", "*.svg"),
                ("JPEG", "*.jpg"),
                ("Все файлы", "*.*"),
            ],
        )
        if not path:
            return
        self.figure.savefig(path, bbox_inches="tight")
