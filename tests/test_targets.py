import pytest
from rebalance.core import validate_targets

def test_validate_targets_normalizes():
    out = validate_targets({"AAPL": 2, "SPY": 2})
    assert out["AAPL"] == pytest.approx(0.5)
    assert out["SPY"] == pytest.approx(0.5)

def test_validate_targets_rejects_negative():
    with pytest.raises(ValueError):
        validate_targets({"AAPL": -0.1})

def test_validate_targets_rejects_empty():
    with pytest.raises(ValueError):
        validate_targets({})
