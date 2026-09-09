from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from ..config import PREDICTIONS_PATH, EQUITY_AUDIT_PATH, BRIEF_OUTPUT_DIR
from python.pdf.generator import generate_brief

router = APIRouter()

@router.get("/brief")
def get_brief(month: str = Query(...), top_n: int = Query(50)):
    filename = f"brief_{month.replace('-', '_')}.pdf"
    output_path = BRIEF_OUTPUT_DIR / filename

    generate_brief(
        str(PREDICTIONS_PATH),
        str(EQUITY_AUDIT_PATH),
        str(output_path),
        top_n=top_n,
        forecast_month=month,
    )

    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename=filename,
    )
