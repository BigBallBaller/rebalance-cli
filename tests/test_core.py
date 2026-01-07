import pandas as pd
from rebalance.core import compute_rebalance

def test_compute_rebalance_basic():
    holdings = pd.DataFrame(
        {"ticker": ["AAPL", "SPY", "TSLA"], "shares": [10, 5, 2], "price": [200, 500, 250]}
    )
    targets = {"AAPL": 0.5, "SPY": 0.4, "TSLA": 0.1}

    df = compute_rebalance(holdings, targets, cash=1000, whole_shares=False)

    assert set(["ticker", "trade_shares", "trade_value", "weight_after"]).issubset(df.columns)
    assert len(df) == 3
