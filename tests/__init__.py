import pandas as pd

from rebalance.core import compute_rebalance


def test_targets_normalize_to_one():
    holdings = pd.DataFrame(
        {"ticker": ["AAPL"], "shares": [1.0], "price": [100.0]}
    )
    targets = {"AAPL": 2.0}  # should normalize to 1.0 internally

    df = compute_rebalance(holdings=holdings, targets=targets, cash=0.0)

    # target_w should sum to 1.0 across rows in holdings that are in the plan table
    assert abs(float(df["target_w"].sum()) - 1.0) < 1e-9


def test_plan_does_not_overspend_cash():
    holdings = pd.DataFrame(
        {"ticker": ["AAPL", "SPY"], "shares": [1.0, 1.0], "price": [100.0, 100.0]}
    )
    targets = {"AAPL": 1.0, "SPY": 0.0}

    df = compute_rebalance(holdings=holdings, targets=targets, cash=0.0)

    # if this ever goes negative, you bought more than you could fund
    assert float(df["cash_after"].iloc[0]) >= -1e-9


def test_whole_shares_trades_are_integers():
    holdings = pd.DataFrame(
        {"ticker": ["AAPL", "SPY"], "shares": [10.0, 10.0], "price": [101.0, 103.0]}
    )
    targets = {"AAPL": 0.7, "SPY": 0.3}

    df = compute_rebalance(holdings=holdings, targets=targets, cash=50.0, whole_shares=True)

    # trade_shares should be whole numbers when whole_shares=True
    assert df["trade_shares"].apply(lambda x: float(x).is_integer()).all()