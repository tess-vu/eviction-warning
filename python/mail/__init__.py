import json
from datetime import datetime
from pathlib import Path

OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "outputs"

def month_label(forecast_month: str) -> str:
    return datetime.strptime(forecast_month, "%Y-%m").strftime("%B %Y")

def append_jsonl(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
