from __future__ import annotations

import json
import pandas as pd


def read_holdings_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"ticker", "shares", "price"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Holdings CSV missing columns: {sorted(missing)}")

    df = df.copy()
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["shares"] = df["shares"].astype(float)
    df["price"] = df["price"].astype(float)

    if (df["shares"] < 0).any():
        raise ValueError("Holdings cannot have negative shares.")
    if (df["price"] <= 0).any():
        raise ValueError("Prices must be > 0.")

    return df


def read_target_json(path: str) -> dict[str, float]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "targets" not in data:
        raise ValueError('Target JSON must look like {"targets": {"AAPL": 0.4}}')

    targets = data["targets"]
    if not isinstance(targets, dict):
        raise ValueError('"targets" must be a JSON object/dict.')

    out: dict[str, float] = {}
    for k, v in targets.items():
        out[str(k).strip().upper()] = float(v)

    return out


def parse_target_string(s: str) -> dict[str, float]:
    # Example: "AAPL=0.5,SPY=0.4,TSLA=0.1"
    out: dict[str, float] = {}
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        raise ValueError("Target string is empty.")

    for part in parts:
        if "=" not in part:
            raise ValueError(f"Bad target pair: {part} (expected TICKER=WEIGHT)")
        k, v = part.split("=", 1)
        out[k.strip().upper()] = float(v)

    return out