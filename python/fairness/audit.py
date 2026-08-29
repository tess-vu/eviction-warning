import argparse
import json
import sys
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from .metrics import mean_observed, mean_predicted, mean_signed_error

# Equity thresholds, fail audit if worst-group MAE minus best-group MAE exceeds this,
# or if mean bias < UNDERPREDICTION_THRESHOLD in any protected group (Black, Hispanic).
MAX_EQUITY_GAP_MAE = 1.5
UNDERPREDICTION_THRESHOLD = -1.0

REQUIRED_COLUMNS = {
    "GEOID", "date", "neighborhood", "racial_majority",
    "filings_count", "predicted", "residual", "abs_error", "bias",
    "risk_quintile", "risk_category", "action_tier",
    "spatial_lag_tier", "spatial_lag_filings", "tax_stress",
    "delinquent_prop_count", "pct_renter", "poverty_rate",
    "severe_rent_burden", "pct_single_mother", "median_income",
    "moratorium_active", "is_extreme_spike", "filings_ma3",
}

EXPECTED_RACIAL_GROUPS = {"White", "Black", "Hispanic", "Asian", "Other"}

class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.generic):
            return obj.item()
        return super().default(obj)

def run_audit(predictions_path: str, output_path: str) -> dict:
    df = pd.read_csv(predictions_path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    actual_groups = set(df["racial_majority"].unique())
    unexpected = actual_groups - EXPECTED_RACIAL_GROUPS
    if unexpected:
        raise ValueError(
            f"Unexpected racial_majority values: {sorted(unexpected)}. "
            f"Expected only: {sorted(EXPECTED_RACIAL_GROUPS)}"
        )

    y_true = df["filings_count"]
    y_pred = df["predicted"]
    sensitive = df["racial_majority"]

    metrics = {
        "MAE": mean_absolute_error,
        "bias": mean_signed_error,
        "RMSE": root_mean_squared_error,
        "mean_observed": mean_observed,
        "mean_predicted": mean_predicted,
    }

    mf = MetricFrame(
        metrics=metrics,
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=sensitive,
    )

    overall = {k: float(v) for k, v in mf.overall.items()}

    by_group_df = mf.by_group.reset_index()
    if "sensitive_feature_0" in by_group_df.columns:
        by_group_df = by_group_df.rename(columns={"sensitive_feature_0": "racial_majority"})
    by_group = [dict(row) for row in by_group_df.to_dict(orient="records")]

    group_mae = mf.by_group["MAE"]
    equity_gap_mae = float(group_mae.max() - group_mae.min())

    group_bias = mf.by_group["bias"]
    underprediction_groups = sorted(
        str(g) for g in group_bias.index if group_bias[g] < UNDERPREDICTION_THRESHOLD
    )

    protected_underprediction = [
        g for g in underprediction_groups if g in ("Black", "Hispanic")
    ]
    passed = equity_gap_mae < MAX_EQUITY_GAP_MAE and len(protected_underprediction) == 0

    forecast_month = pd.to_datetime(df["date"]).max().strftime("%Y-%m")

    report = {
        "run_date": str(date.today()),
        "forecast_month": forecast_month,
        "overall": overall,
        "by_group": by_group,
        "equity_gap_mae": equity_gap_mae,
        "systematic_underprediction_groups": underprediction_groups,
        "passed_equity_check": bool(passed),
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, cls=_NumpyEncoder)

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run fairness audit on eviction predictions")
    parser.add_argument("--predictions", required=True, help="Path to model_predictions.csv")
    parser.add_argument("--output", required=True, help="Path for equity_audit.json output")
    args = parser.parse_args()

    result = run_audit(args.predictions, args.output)
    gap = result["equity_gap_mae"]
    passed = result["passed_equity_check"]
    groups = result["systematic_underprediction_groups"]
    print(f"Equity audit complete. Passed: {passed} | MAE Gap: {gap:.3f}")
    if groups:
        print(f"Under-Prediction Groups: {groups}")
    if not passed:
        sys.exit(1)
