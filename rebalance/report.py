from __future__ import annotations

import pandas as pd
from rich.console import Console
from rich.table import Table


def _fmt_money(x: float) -> str:
    sign = "-" if x < 0 else ""
    x = abs(x)
    return f"{sign}${x:,.2f}"


def _fmt_pct(x: float) -> str:
    return f"{x*100:.2f}%"


def print_report(df: pd.DataFrame) -> None:
    console = Console()
    table = Table(title="Rebalance Plan")

    columns = [
        ("ticker", "Ticker"),
        ("price", "Price"),
        ("shares", "Shares"),
        ("value", "Value"),
        ("current_w", "Cur W"),
        ("target_w", "Tgt W"),
        ("action", "Action"),
        ("trade_shares", "Trade Sh"),
        ("trade_value", "Trade $"),
        ("weight_after", "After W"),
    ]

    for _, label in columns:
        table.add_column(label, justify="right")

    for _, r in df.iterrows():
        table.add_row(
            str(r["ticker"]),
            _fmt_money(float(r["price"])),
            f"{float(r['shares']):,.4g}",
            _fmt_money(float(r["value"])),
            _fmt_pct(float(r["current_w"])),
            _fmt_pct(float(r["target_w"])),
            str(r["action"]),
            f"{float(r['trade_shares']):,.4g}",
            _fmt_money(float(r["trade_value"])),
            _fmt_pct(float(r["weight_after"])),
        )

    console.print(table)

    # Cash summary (same for all rows)
    cash_before = float(df["cash_before"].iloc[0])
    cash_after = float(df["cash_after"].iloc[0])
    net_used = float(df["net_cash_used"].iloc[0])

    console.print(f"\nCash before: {_fmt_money(cash_before)}")
    console.print(f"Net cash used: {_fmt_money(net_used)}")
    console.print(f"Cash after: {_fmt_money(cash_after)}\n")