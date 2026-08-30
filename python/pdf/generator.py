import argparse
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

TEMPLATES_DIR = Path(__file__).parent / "templates"
ASSETS_DIR = Path(__file__).parent / "assets"

def _action_tier(predicted):
    if predicted >= 12:
        return "Deploy Canvassers"
    if predicted >= 8:
        return "Direct Mail"
    if predicted >= 5:
        return "Legal Aid Pop-Up"
    return "Monitor"

def _spatial_lag_tier(value):
    if pd.isna(value):
        return "N/A"
    if value < 2:
        return "Low"
    if value <= 5:
        return "Moderate"
    return "High"

def _equity_summary(audit):
    if audit["passed_equity_check"]:
        return "The equity check passed. No groups show systematic under-prediction."
    groups = audit["systematic_underprediction_groups"]
    sentences = [
        f"{g} tracts show systematic under-prediction (bias below −1.0)."
        for g in groups
    ]
    return "The equity check did not pass. " + " ".join(sentences)

def _build_context(predictions_path, equity_audit_path, top_n, forecast_month):
    df = pd.read_csv(predictions_path, dtype={"GEOID": str})
    with open(equity_audit_path) as f:
        audit = json.load(f)

    df["date"] = pd.to_datetime(df["date"])
    if forecast_month is None:
        forecast_month = df["date"].max().strftime("%Y-%m")

    month_df = df[df["date"].dt.strftime("%Y-%m") == forecast_month].copy()
    if month_df.empty:
        raise ValueError(f"No data for forecast month {forecast_month}")

    month_df = month_df.sort_values("predicted", ascending=False)
    month_df["_action_tier"] = month_df["predicted"].apply(_action_tier)

    if "spatial_lag_filings" in month_df.columns:
        month_df["_lag_tier"] = month_df["spatial_lag_filings"].apply(_spatial_lag_tier)
    else:
        month_df["_lag_tier"] = "N/A"

    critical = month_df[month_df["predicted"] > 12]
    top = month_df.head(top_n)
    city_median = month_df["delinquent_prop_count"].median()
    tax_overlap = (
        (critical["delinquent_prop_count"] > city_median).mean()
        if len(critical) else 0.0
    )

    tracts = []
    for rank, (_, row) in enumerate(top.iterrows(), 1):
        tracts.append({
            "rank": rank,
            "geoid": row["GEOID"],
            "neighborhood": row["neighborhood"],
            "predicted": round(row["predicted"], 1),
            "spatial_lag_tier": row["_lag_tier"],
            "tax_stress": row["tax_stress"],
            "racial_majority": row["racial_majority"],
            "action_tier": row["_action_tier"],
        })

    equity_groups = []
    for g in audit["by_group"]:
        bias = g["bias"]
        equity_groups.append({
            "group": g["racial_majority"],
            "mae": round(g["MAE"], 3),
            "bias": round(bias, 3),
            "mean_observed": round(g["mean_observed"], 2),
            "mean_predicted": round(g["mean_predicted"], 2),
            "equity_flag": "\u26a0 Under-prediction" if bias < -1.0 else "\u2713",
        })

    passed = audit["passed_equity_check"]
    return {
        "forecast_month": forecast_month,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "model_mae": round(audit["overall"]["MAE"], 3),
        "passed_equity_check": passed,
        "banner_color": "#2176D2" if passed else "#F3A738",
        "banner_text": "EQUITY CHECK PASSED" if passed else "EQUITY REVIEW REQUIRED",
        "n_critical": len(critical),
        "predicted_filings_top_n": round(top["predicted"].sum(), 1),
        "tax_delinquency_overlap": round(tax_overlap * 100, 1),
        "top_n": top_n,
        "tracts": tracts,
        "equity_groups": equity_groups,
        "equity_summary": _equity_summary(audit),
        "has_logo": (ASSETS_DIR / "philly_logo.png").exists(),
        "model_version": "NB-v1.0",
    }

def _render_html(ctx):
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    return env.get_template("brief.html").render(**ctx)

def generate_brief(predictions_path: str, equity_audit_path: str, output_path: str,
                   top_n: int = 50, forecast_month: str = None) -> str:
    ctx = _build_context(predictions_path, equity_audit_path, top_n, forecast_month)
    html_string = _render_html(ctx)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_string, base_url=str(ASSETS_DIR.resolve())).write_pdf(output_path)
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate monthly triage brief PDF")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--equity-audit", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--top-n", type=int, default=50)
    parser.add_argument("--forecast-month", default=None)
    args = parser.parse_args()

    path = generate_brief(
        args.predictions, args.equity_audit, args.output,
        top_n=args.top_n, forecast_month=args.forecast_month,
    )
    print(f"Brief written to {path}")
