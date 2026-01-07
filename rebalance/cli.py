from __future__ import annotations

import typer

from rebalance.core import compute_rebalance
from rebalance.io import parse_target_string, read_holdings_csv, read_target_json
from rebalance.report import print_report

app = typer.Typer(help="Portfolio rebalancing CLI", no_args_is_help=True)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Portfolio rebalancing CLI."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def plan(
    holdings: str = typer.Option(..., "--holdings", "-h", help="Path to holdings CSV (ticker, shares, price)"),
    target_json: str | None = typer.Option(None, "--target-json", help='Path to JSON: {"targets": {"AAPL": 0.4}}'),
    target: str | None = typer.Option(None, "--target", help='Target string like "AAPL=0.4,SPY=0.6"'),
    cash: float = typer.Option(0.0, "--cash", help="Cash included in total portfolio value"),
    whole_shares: bool = typer.Option(False, "--whole-shares", help="Round trades to whole shares"),
    min_trade_dollars: float = typer.Option(0.0, "--min-trade", help="Ignore trades smaller than this dollar amount"),
    tolerance_pct: float = typer.Option(0.0, "--tolerance", help="Ignore changes where |drift| < tolerance percent"),
    out_csv: str | None = typer.Option(None, "--out", help="Write the plan to a CSV file"),
) -> None:
    """Create a rebalance plan from current holdings and a target allocation."""
    if (target_json is None) == (target is None):
        raise typer.BadParameter("Provide exactly one: --target-json OR --target")

    targets = read_target_json(target_json) if target_json else parse_target_string(target)  # type: ignore[arg-type]
    df_holdings = read_holdings_csv(holdings)

    plan_df = compute_rebalance(
        holdings=df_holdings,
        targets=targets,
        cash=cash,
        whole_shares=whole_shares,
        min_trade_dollars=min_trade_dollars,
        tolerance_pct=tolerance_pct,
    )

    print_report(plan_df)

    if out_csv:
        plan_df.to_csv(out_csv, index=False)
        typer.echo(f"Wrote CSV: {out_csv}")