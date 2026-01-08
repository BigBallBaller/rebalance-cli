# rebalance-cli

A Python command-line tool that generates a **buy/sell portfolio rebalancing plan**
from current holdings and target asset allocations.

Given a CSV of holdings and desired target weights, `rebalance-cli` calculates how
many shares to buy or sell to realign the portfolio, optionally respecting whole-share
constraints and cash limits.

---

## Features

- Reads current holdings from a CSV file
- Supports target allocations via JSON or inline string
- Accounts for available cash in the rebalance
- Optional whole-share trading mode
- Clean terminal output using Rich tables
- Tested with pytest and validated via GitHub Actions CI

---

## Installation

```bash
git clone https://github.com/BigBallBaller/rebalance-cli.git
cd rebalance-cli

python -m venv .venv
source .venv/bin/activate
pip install -e .