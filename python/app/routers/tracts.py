import pandas as pd
from fastapi import APIRouter, Query
from ..data import load_predictions, load_equity_audit
from ..schemas import TractsResponse, TractRecord, KPISummary

router = APIRouter()

ACTION_TIERS = [(12, "Deploy Canvassers"), (8, "Direct Mail"), (5, "Legal Aid Pop-Up")]

def _action_tier(predicted: float) -> str:
    for threshold, label in ACTION_TIERS:
        if predicted >= threshold:
            return label
    return "Monitor"

def _spatial_lag_tier(value) -> str:
    if pd.isna(value):
        return "N/A"
    if value < 2:
        return "Low"
    if value <= 5:
        return "Moderate"
    return "High"

@router.get("/tracts", response_model=TractsResponse)
def get_tracts(month: str = Query(...), top_n: int = Query(50)):
    df = load_predictions()
    df["date"] = pd.to_datetime(df["date"])
    month_df = df[df["date"].dt.strftime("%Y-%m") == month].copy()
    if month_df.empty:
        return TractsResponse(
            month=month, top_n=top_n,
            kpi=KPISummary(
                critical_tracts=0, predicted_filings_top_n=0,
                model_mae=0, equity_passed=False, equity_label="No data", top_n=top_n,
            ),
            tracts=[],
        )

    month_df = month_df.sort_values("predicted", ascending=False)

    audit = load_equity_audit()
    passed = audit.get("passed_equity_check", False)
    mae = round(audit["overall"]["MAE"], 3)

    critical = month_df[month_df["predicted"] > 12]
    top = month_df.head(top_n)

    tracts = []
    for rank, (_, row) in enumerate(top.iterrows(), 1):
        lag = row.get("spatial_lag_filings")
        tracts.append(TractRecord(
            rank=rank,
            geoid=row["GEOID"],
            neighborhood=row["neighborhood"],
            predicted=round(row["predicted"], 1),
            action_tier=_action_tier(row["predicted"]),
            racial_majority=row["racial_majority"],
            tax_stress=row["tax_stress"],
            risk_quintile=int(row["risk_quintile"]),
            spatial_lag_tier=_spatial_lag_tier(lag),
        ))

    kpi = KPISummary(
        critical_tracts=len(critical),
        predicted_filings_top_n=round(top["predicted"].sum(), 1),
        model_mae=mae,
        equity_passed=passed,
        equity_label="✓ Passed" if passed else "⚠ Review required",
        top_n=top_n,
    )

    return TractsResponse(month=month, top_n=top_n, kpi=kpi, tracts=tracts)
