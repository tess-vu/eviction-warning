import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from starlette.status import HTTP_202_ACCEPTED
from ..config import PREDICTIONS_PATH, SUBSCRIBERS_PATH, MOCK_OUTBOUND
from ..schemas import CampaignRequest, CampaignAccepted

router = APIRouter()
log = logging.getLogger(__name__)

def _run_campaign(predictions_path: str, subscribers_path: str,
                  forecast_month: str, top_n: int, mock_outbound: bool):
    # TODO: swap BackgroundTasks for a proper task queue (Celery/arq) in production
    try:
        from python.mail.campaign import run_monthly_campaign
        run_monthly_campaign(
            predictions_path=predictions_path,
            subscribers_path=subscribers_path,
            forecast_month=forecast_month,
            top_n=top_n,
            dry_run=False,
            mock_outbound=mock_outbound,
        )
    except ImportError:
        log.warning("Mail module not yet available. Campaign skipped.")
    except Exception:
        log.exception("Campaign failed.")

@router.post("/campaign", status_code=HTTP_202_ACCEPTED, response_model=CampaignAccepted)
def start_campaign(body: CampaignRequest, tasks: BackgroundTasks):
    job_id = f"campaign_{body.month.replace('-', '_')}"
    tasks.add_task(
        _run_campaign,
        predictions_path=str(PREDICTIONS_PATH),
        subscribers_path=str(SUBSCRIBERS_PATH),
        forecast_month=body.month,
        top_n=body.top_n,
        mock_outbound=MOCK_OUTBOUND,
    )
    return CampaignAccepted(job_id=job_id, status="started")
