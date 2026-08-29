import json
import numpy as np
import pandas as pd
import pytest
from python.fairness.audit import run_audit

def _synthetic_df(seed=42):
    """30 rows across 4 racial groups with well-behaved predictions."""
    rng = np.random.default_rng(seed)
    groups = ["White"] * 8 + ["Black"] * 8 + ["Hispanic"] * 7 + ["Asian"] * 7
    n = len(groups)
    observed = rng.integers(0, 10, size=n)
    predicted = observed + rng.normal(0, 0.5, size=n)

    return pd.DataFrame({
        "GEOID": [f"421010{i:04d}" for i in range(n)],
        "date": "2024-06-01",
        "neighborhood": "TestNeighborhood",
        "racial_majority": groups,
        "filings_count": observed,
        "predicted": predicted,
        "residual": observed - predicted,
        "abs_error": np.abs(observed - predicted),
        "bias": predicted - observed,
        "risk_quintile": rng.integers(1, 6, size=n),
        "risk_category": "Moderate Risk",
        "action_tier": "Monitor",
        "spatial_lag_tier": "Low",
        "spatial_lag_filings": rng.uniform(0, 10, size=n),
        "tax_stress": "No",
        "delinquent_prop_count": rng.integers(0, 100, size=n),
        "pct_renter": rng.uniform(20, 90, size=n),
        "poverty_rate": rng.uniform(5, 40, size=n),
        "severe_rent_burden": rng.uniform(10, 50, size=n),
        "pct_single_mother": rng.uniform(5, 30, size=n),
        "median_income": rng.integers(20000, 80000, size=n),
        "moratorium_active": 0,
        "is_extreme_spike": 0,
        "filings_ma3": rng.uniform(0, 5, size=n),
    })

def test_json_has_all_required_keys(tmp_path):
    df = _synthetic_df()
    csv_path = tmp_path / "preds.csv"
    json_path = tmp_path / "audit.json"
    df.to_csv(csv_path, index=False)

    result = run_audit(str(csv_path), str(json_path))

    assert {"run_date", "forecast_month", "overall", "by_group",
            "equity_gap_mae", "systematic_underprediction_groups",
            "passed_equity_check"} <= set(result.keys())
    assert json_path.exists()
    with open(json_path) as f:
        written = json.load(f)
    assert written == result

def test_by_group_contains_all_groups(tmp_path):
    df = _synthetic_df()
    csv_path = tmp_path / "preds.csv"
    json_path = tmp_path / "audit.json"
    df.to_csv(csv_path, index=False)

    result = run_audit(str(csv_path), str(json_path))
    group_names = {row["racial_majority"] for row in result["by_group"]}
    assert group_names == {"White", "Black", "Hispanic", "Asian"}

def test_black_underprediction_triggers_flag(tmp_path):
    df = _synthetic_df()
    mask = df["racial_majority"] == "Black"
    df.loc[mask, "predicted"] = df.loc[mask, "filings_count"] - 3.0
    csv_path = tmp_path / "preds.csv"
    json_path = tmp_path / "audit.json"
    df.to_csv(csv_path, index=False)

    result = run_audit(str(csv_path), str(json_path))

    assert "Black" in result["systematic_underprediction_groups"]
    assert result["passed_equity_check"] is False

def test_missing_column_raises_valueerror(tmp_path):
    df = _synthetic_df().drop(columns=["racial_majority"])
    csv_path = tmp_path / "preds.csv"
    df.to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        run_audit(str(csv_path), str(tmp_path / "audit.json"))

def test_unexpected_racial_group_raises_valueerror(tmp_path):
    df = _synthetic_df()
    df.loc[0, "racial_majority"] = "Martian"
    csv_path = tmp_path / "preds.csv"
    df.to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Unexpected racial_majority"):
        run_audit(str(csv_path), str(tmp_path / "audit.json"))
