from fastapi import APIRouter, Query
from ..data import load_equity_audit
from ..schemas import EquityResponse, EquityGroup

router = APIRouter()

UNDERPREDICTION_THRESHOLD = -1.0

def _build_narrative(audit: dict) -> str:
    if audit["passed_equity_check"]:
        return "All groups show acceptable bias. No group is systematically under-predicted."
    groups = audit["systematic_underprediction_groups"]
    sentences = [f"{g} tracts show systematic under-prediction (bias below −1.0)." for g in groups]
    return "Equity check did not pass. " + " ".join(sentences)

@router.get("/equity", response_model=EquityResponse)
def get_equity(month: str = Query(...)):
    audit = load_equity_audit()

    groups = []
    for g in audit["by_group"]:
        bias = g["bias"]
        groups.append(EquityGroup(
            group=g["racial_majority"],
            mae=round(g["MAE"], 3),
            bias=round(bias, 3),
            mean_observed=round(g["mean_observed"], 2),
            mean_predicted=round(g["mean_predicted"], 2),
            equity_flag="⚠ Under-prediction" if bias < UNDERPREDICTION_THRESHOLD else "✓",
        ))

    return EquityResponse(
        month=month,
        passed=audit["passed_equity_check"],
        equity_gap_mae=round(audit["equity_gap_mae"], 3),
        narrative=_build_narrative(audit),
        groups=groups,
    )
