import pandas as pd
from rebalance.core import compute_rebalance

def test_whole_shares_trades_are_integers_and_cash_nonnegative():
    holdings = pd.DataFrame(
        {"ticker": ["AAPL", "SPY", "TSLA"], "shares": [10, 5, 2], "price": [200.0, 500.0, 250.0]}
    )
    targets = {"AAPL": 0.5, "SPY": 0.4, "TSLA": 0.1}

    df = compute_rebalance(
        holdings=holdings,
        targets=targets,
        cash=1000.0,
        whole_shares=True,
    )

    # whole_shares=True => trade_shares should be whole numbers
    assert df["trade_shares"].apply(lambda x: float(x).is_integer()).all()

    # should never overspend cash
    assert float(df["cash_after"].iloc[0]) >= -1e-9
