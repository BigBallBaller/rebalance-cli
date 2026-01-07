from __future__ import annotations

import math
import pandas as pd


def validate_targets(targets: dict[str, float]) -> dict[str, float]:
    if not targets:
        raise ValueError("No targets provided.")

    for t, w in targets.items():
        if w < 0:
            raise ValueError(f"Target weight cannot be negative: {t}={w}")

    total = float(sum(targets.values()))
    if total <= 0:
        raise ValueError("Sum of target weights must be > 0.")

    # Normalize to sum to 1.0
    return {t: float(w) / total for t, w in targets.items()}


def compute_rebalance(
    holdings: pd.DataFrame,
    targets: dict[str, float],
    cash: float = 0.0,
    whole_shares: bool = False,
    min_trade_dollars: float = 0.0,
    tolerance_pct: float = 0.0,
) -> pd.DataFrame:
    if cash < -1e-9:
        raise ValueError("cash cannot be negative in this MVP.")

    targets = validate_targets(targets)

    df = holdings.copy()
    df["value"] = df["shares"] * df["price"]

    total_value = float(df["value"].sum()) + float(cash)
    if total_value <= 0:
        raise ValueError("Total portfolio value must be > 0.")

    df["target_w"] = df["ticker"].map(targets).fillna(0.0)
    df["current_w"] = df["value"] / total_value
    df["target_value"] = df["target_w"] * total_value
    df["delta_value"] = df["target_value"] - df["value"]

    if tolerance_pct > 0:
        drift = (df["target_w"] - df["current_w"]).abs()
        df.loc[drift < (float(tolerance_pct) / 100.0), "delta_value"] = 0.0

    df["trade_shares_raw"] = df["delta_value"] / df["price"]

    # ---------- Decide trade_shares ----------
    if whole_shares:
        # Start with no trades
        df["trade_shares"] = 0.0
        cash_available = float(cash)

        # Compute overweight/underweight in dollars
        df["excess_value"] = (df["value"] - df["target_value"]).clip(lower=0.0)

        # 1) SELL overweight (whole shares) to raise cash
        for idx, row in df.sort_values("excess_value", ascending=False).iterrows():
            if float(row["excess_value"]) <= 0:
                continue

            price = float(row["price"])
            shares_owned = float(row["shares"])

            max_sell_shares = int(math.floor(float(row["excess_value"]) / price))
            max_sell_shares = min(max_sell_shares, int(shares_owned))
            if max_sell_shares <= 0:
                continue

            df.at[idx, "trade_shares"] = float(-max_sell_shares)
            cash_available += float(max_sell_shares) * price

        df["trade_value"] = df["trade_shares"] * df["price"]

        # Optional: drop tiny trades (including sells)
        if min_trade_dollars > 0:
            small = df["trade_value"].abs() < float(min_trade_dollars)
            df.loc[small, ["trade_shares", "trade_value"]] = 0.0

        # Recompute available cash after the filter
        total_buy_dollars = float(df.loc[df["trade_value"] > 0, "trade_value"].sum())
        total_sell_dollars = float((-df.loc[df["trade_value"] < 0, "trade_value"]).sum())
        cash_available = float(cash) - total_buy_dollars + total_sell_dollars

        # 2) BUY underweight (1 share at a time), greedily
        df["value_tmp"] = df["value"] + (df["trade_shares"] * df["price"])
        df["gap_value"] = (df["target_value"] - df["value_tmp"]).clip(lower=0.0)

        while True:
            affordable = df[(df["gap_value"] > 0) & (df["price"] <= cash_available)]
            if affordable.empty:
                break

            idx = affordable["gap_value"].idxmax()
            price = float(df.at[idx, "price"])

            df.at[idx, "trade_shares"] = float(df.at[idx, "trade_shares"]) + 1.0
            cash_available -= price

            df.at[idx, "value_tmp"] = float(df.at[idx, "value_tmp"]) + price
            df.at[idx, "gap_value"] = max(
                0.0,
                float(df.at[idx, "target_value"]) - float(df.at[idx, "value_tmp"]),
            )

        # Final cash summary
        df["trade_value"] = df["trade_shares"] * df["price"]
        total_buy_dollars = float(df.loc[df["trade_value"] > 0, "trade_value"].sum())
        total_sell_dollars = float((-df.loc[df["trade_value"] < 0, "trade_value"]).sum())
        net_cash_used = total_buy_dollars - total_sell_dollars
        cash_after = float(cash) - net_cash_used

        df.drop(columns=["excess_value", "value_tmp", "gap_value"], inplace=True)

    else:
        df["trade_shares"] = df["trade_shares_raw"]
        df["trade_value"] = df["trade_shares"] * df["price"]

        if min_trade_dollars > 0:
            small = df["trade_value"].abs() < float(min_trade_dollars)
            df.loc[small, ["trade_shares", "trade_value", "delta_value"]] = 0.0

        total_buy_dollars = float(df.loc[df["trade_value"] > 0, "trade_value"].sum())
        total_sell_dollars = float((-df.loc[df["trade_value"] < 0, "trade_value"]).sum())
        net_cash_used = total_buy_dollars - total_sell_dollars
        cash_after = float(cash) - net_cash_used

    # ---------- Post-trade portfolio ----------
    df["action"] = df["trade_shares"].apply(
        lambda x: "BUY" if x > 0 else ("SELL" if x < 0 else "HOLD")
    )

    df["shares_after"] = df["shares"] + df["trade_shares"]
    df["value_after"] = df["shares_after"] * df["price"]
    df["weight_after"] = df["value_after"] / total_value

    df["cash_before"] = float(cash)
    df["cash_after"] = float(cash_after)
    df["net_cash_used"] = float(net_cash_used)

    return df[
        [
            "ticker",
            "price",
            "shares",
            "value",
            "current_w",
            "target_w",
            "target_value",
            "delta_value",
            "action",
            "trade_shares",
            "trade_value",
            "shares_after",
            "value_after",
            "weight_after",
            "cash_before",
            "cash_after",
            "net_cash_used",
        ]
    ].copy()