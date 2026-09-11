import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
import pandas as pd
from .config import PREDICTIONS_PATH, EQUITY_AUDIT_PATH

@lru_cache(maxsize=1)
def _load_predictions_raw(mtime: float) -> pd.DataFrame:
    return pd.read_csv(PREDICTIONS_PATH, dtype={"GEOID": str})

@lru_cache(maxsize=1)
def _load_equity_raw(mtime: float) -> dict:
    with open(EQUITY_AUDIT_PATH) as f:
        return json.load(f)

def load_predictions() -> pd.DataFrame:
    mtime = PREDICTIONS_PATH.stat().st_mtime
    return _load_predictions_raw(mtime)

def load_equity_audit() -> dict:
    mtime = EQUITY_AUDIT_PATH.stat().st_mtime
    return _load_equity_raw(mtime)

def available_months() -> list[str]:
    df = load_predictions()
    months = pd.to_datetime(df["date"]).dt.strftime("%Y-%m").sort_values().unique()
    return sorted(months, reverse=True)

def data_loaded() -> bool:
    return PREDICTIONS_PATH.exists() and EQUITY_AUDIT_PATH.exists()

def last_updated() -> str:
    mtime = max(PREDICTIONS_PATH.stat().st_mtime, EQUITY_AUDIT_PATH.stat().st_mtime)
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
