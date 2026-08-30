import json
import numpy as np
import pandas as pd
import pytest
from python.pdf.generator import generate_brief, _build_context, _render_html

def _test_predictions(n=40, seed=42):
    rng = np.random.default_rng(seed)
    groups = (["White"] * 10 + ["Black"] * 10 + ["Hispanic"] * 10 + ["Asian"] * 10)[:n]

    predicted = np.concatenate([
        rng.uniform(13, 20, size=5),
        rng.uniform(8, 11.9, size=10),
        rng.uniform(5, 7.9, size=10),
        rng.uniform(0, 4.9, size=n - 25),
    ])
    rng.shuffle(predicted)
    observed = (predicted + rng.normal(0, 1, size=n)).clip(0).astype(int)

    return pd.DataFrame({
        "GEOID": [f"421010{i:04d}" for i in range(n)],
        "date": "2024-06-01",
        "neighborhood": rng.choice(
            ["Kensington", "Point Breeze", "Germantown", "Frankford"], size=n,
        ),
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
        "tax_stress": rng.choice(["Yes", "No"], size=n),
        "delinquent_prop_count": rng.integers(0, 200, size=n),
        "pct_renter": rng.uniform(20, 90, size=n),
        "poverty_rate": rng.uniform(5, 40, size=n),
        "severe_rent_burden": rng.uniform(10, 50, size=n),
        "pct_single_mother": rng.uniform(5, 30, size=n),
        "median_income": rng.integers(20000, 80000, size=n),
        "moratorium_active": 0,
        "is_extreme_spike": 0,
        "filings_ma3": rng.uniform(0, 5, size=n),
    })

def _test_audit(passed=True):
    return {
        "run_date": "2026-08-29",
        "forecast_month": "2024-06",
        "overall": {
            "MAE": 1.77, "bias": 0.20, "RMSE": 3.03,
            "mean_observed": 2.64, "mean_predicted": 2.84,
        },
        "by_group": [
            {"racial_majority": "Black", "MAE": 2.22,
             "bias": -1.5 if not passed else 0.31,
             "RMSE": 3.18, "mean_observed": 3.63, "mean_predicted": 3.94},
            {"racial_majority": "Hispanic", "MAE": 1.57, "bias": 0.27,
             "RMSE": 2.03, "mean_observed": 2.51, "mean_predicted": 2.77},
            {"racial_majority": "White", "MAE": 1.31, "bias": 0.03,
             "RMSE": 2.92, "mean_observed": 1.62, "mean_predicted": 1.65},
            {"racial_majority": "Asian", "MAE": 1.50, "bias": 0.15,
             "RMSE": 2.50, "mean_observed": 2.00, "mean_predicted": 2.15},
        ],
        "equity_gap_mae": 0.90,
        "systematic_underprediction_groups": [] if passed else ["Black"],
        "passed_equity_check": passed,
    }

def _write_fixtures(tmp_path, passed=True):
    df = _test_predictions()
    csv_path = tmp_path / "preds.csv"
    df.to_csv(csv_path, index=False)

    audit = _test_audit(passed)
    json_path = tmp_path / "audit.json"
    with open(json_path, "w") as f:
        json.dump(audit, f)

    return str(csv_path), str(json_path)

def test_pdf_exists_and_nonempty(tmp_path):
    csv_path, json_path = _write_fixtures(tmp_path)
    out = tmp_path / "brief.pdf"
    result = generate_brief(csv_path, json_path, str(out), top_n=10)
    assert result == str(out)
    assert out.stat().st_size > 0

def test_banner_passed(tmp_path):
    csv_path, json_path = _write_fixtures(tmp_path, passed=True)
    ctx = _build_context(csv_path, json_path, top_n=10, forecast_month=None)
    assert ctx["banner_color"] == "#2176D2"
    assert ctx["banner_text"] == "Equity check passed."

    html = _render_html(ctx)
    assert "Equity check passed." in html
    assert "#2176D2" in html

def test_banner_failed(tmp_path):
    csv_path, json_path = _write_fixtures(tmp_path, passed=False)
    ctx = _build_context(csv_path, json_path, top_n=10, forecast_month=None)
    assert ctx["banner_color"] == "#F3A738"
    assert ctx["banner_text"] == "Equity review required."

    html = _render_html(ctx)
    assert "Equity review required." in html
    assert "#F3A738" in html
