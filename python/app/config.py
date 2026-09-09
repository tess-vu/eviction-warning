from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PREDICTIONS_PATH = PROJECT_ROOT / "outputs" / "model_predictions.csv"
EQUITY_AUDIT_PATH = PROJECT_ROOT / "outputs" / "equity_audit.json"
BRIEF_OUTPUT_DIR = PROJECT_ROOT / "outputs"
FRONTEND_BUILD_DIR = PROJECT_ROOT / "frontend" / "dist"

PHILLY_TRACTS_GEOJSON_URL = (
    "https://opendata.arcgis.com/datasets/"
    "8bc0786524a4486bb3cf0f9862ad0fbf_0.geojson"
)

SUBSCRIBERS_PATH = PROJECT_ROOT / "data" / "subscribers.csv"
MOCK_OUTBOUND = True
