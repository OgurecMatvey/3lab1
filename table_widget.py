
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List

from backend.models import CurrencyRate


class RatesTable(ttk.Frame):
    """Виджет-таблица со столбцами: Дата | <валюта 1> | <валюта 2> | ..."""

    def __init__(self, master: tk.Widget):
        super().__init__(master)
        self.tree = ttk.Treeview(self, show="headings")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def show(self, rates: List[CurrencyRate]) -> None:
        self.tree.delete(*self.tree.get_children())
        if not rates:
            return

        currencies = list(rates[0].rates.keys())
        columns = ["date"] + currencies
        self.tree["columns"] = columns
        self.tree.heading("date", text="Дата")
        self.tree.column("date", width=110, anchor="center")
        for cur in currencies:
            self.tree.heading(cur, text=f"{cur}, ₽")
            self.tree.column(cur, width=100, anchor="center")

        for rate in rates:
            values = [rate.day.strftime("%d.%m.%Y")] + [
                f"{rate.rates[cur]:.2f}" for cur in currencies
            ]
            self.tree.insert("", "end", values=values)
