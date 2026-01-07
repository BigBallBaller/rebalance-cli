from __future__ import annotations

import typer

from rebalance.core import compute_rebalance
from rebalance.io import parse_target_string, read_holdings_csv, read_target_json
from rebalance.report import print_report

app = typer.Typer(help="Portfolio rebalancing CLI")


@app.command()
def plan(
    holdings: str = typer.Option(..., "--holdings", "-h"),
    target_json: str | None = typer.Option(None, "--target-json"),
    target: str | None = typer.Option(None, "--target"),
    cash: float = typer.Option(0.0, "--cash"),
    whole_shares: bool = typer.Option(False, "--whole-shares"),
    min_trade_dollars: float = typer.Option(0.0, "--min-trade"),
    tolerance_pct: float = typer.Option(0.0, "--tolerance"),
    out_csv: str | None = typer.Option(None, "--out"),
) -> None:
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


def main() -> None:
    app()


if __name__ == "__main__":
    main()