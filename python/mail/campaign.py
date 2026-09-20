import argparse
import json
import logging
import os
import time
from collections import Counter
from pathlib import Path
from typing import Optional
import pandas as pd
from . import OUTPUTS_DIR
from . import direct_mail, email_sender
from .subscribers import get_subscribers_for_tracts, load_subscribers

CRITICAL_THRESHOLD = 12
ACTION_TIERS = [(12, "Deploy Canvassers"), (8, "Direct Mail"), (5, "Legal Aid Pop-Up")]
SEND_DELAY_SECONDS = 0.1

log = logging.getLogger(__name__)

def _action_tier(predicted: float) -> str:
    for threshold, label in ACTION_TIERS:
        if predicted >= threshold:
            return label
    return "Monitor"

def _critical_tracts(predictions_path: str, forecast_month: str, top_n: int) -> pd.DataFrame:
    df = pd.read_csv(predictions_path, dtype={"GEOID": str})
    df["date"] = pd.to_datetime(df["date"])
    month_df = df[df["date"].dt.strftime("%Y-%m") == forecast_month]
    if month_df.empty:
        raise ValueError(f"No predictions for forecast month {forecast_month}.")

    ranked = month_df.sort_values("predicted", ascending=False).head(top_n)
    return ranked[ranked["predicted"] > CRITICAL_THRESHOLD]

def _write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

def run_monthly_campaign(
    predictions_path: str,
    subscribers_path: str,
    forecast_month: str,
    top_n: int = 50,
    dry_run: bool = True,
    mock_outbound: bool = True,
    sendgrid_api_key: Optional[str] = None,
    lob_api_key: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> dict:
    out_dir = Path(output_dir or OUTPUTS_DIR)
    slug = forecast_month.replace("-", "_")

    if not dry_run and not mock_outbound and not (sendgrid_api_key and lob_api_key):
        raise ValueError(
            "Live sends require both a SendGrid and a Lob API key. "
            "Pass mock_outbound=True to run against the local logs instead."
        )

    critical = _critical_tracts(predictions_path, forecast_month, top_n)
    tier_by_geoid = {
        row.GEOID: _action_tier(row.predicted) for row in critical.itertuples()
    }
    predicted_by_geoid = {row.GEOID: row.predicted for row in critical.itertuples()}

    send_list = get_subscribers_for_tracts(load_subscribers(subscribers_path), tier_by_geoid)

    if dry_run:
        for s in send_list:
            log.info(
                "Would notify %s in tract %s via %s (%s)",
                s.subscriber_id, s.GEOID, s.channel, tier_by_geoid[s.GEOID],
            )
        report = {
            "forecast_month": forecast_month,
            "target_tracts": sorted(tier_by_geoid),
            "total_eligible_subscribers": len(send_list),
            "subscribers_by_channel": dict(Counter(s.channel for s in send_list)),
            "dry_run": True,
        }
        _write_report(out_dir / f"campaign_dry_run_{slug}.json", report)
        return report

    if not send_list:
        raise ValueError(
            "No opted-in subscribers fall inside the targeted tracts. "
            "The campaign will not send to anyone who has not opted in."
        )

    sent = 0
    failed_ids = []

    for subscriber in send_list:
        tier = tier_by_geoid[subscriber.GEOID]
        delivered = True

        if subscriber.wants_email:
            try:
                delivered = email_sender.send_notification(
                    subscriber,
                    tier,
                    predicted_by_geoid[subscriber.GEOID],
                    forecast_month,
                    api_key=sendgrid_api_key,
                    mock=mock_outbound,
                    output_dir=out_dir,
                ) and delivered
            except Exception:
                log.exception("Email failed for subscriber %s.", subscriber.subscriber_id)
                delivered = False
            if not mock_outbound:
                time.sleep(SEND_DELAY_SECONDS)

        if subscriber.wants_mail:
            try:
                direct_mail.send_letter(
                    subscriber,
                    tier,
                    forecast_month,
                    api_key=lob_api_key,
                    mock=mock_outbound,
                    output_dir=out_dir,
                )
            except Exception:
                log.exception("Letter failed for subscriber %s.", subscriber.subscriber_id)
                delivered = False

        if delivered:
            sent += 1
        else:
            failed_ids.append(subscriber.subscriber_id)

    report = {
        "forecast_month": forecast_month,
        "target_tracts": sorted(tier_by_geoid),
        "total_targeted": len(send_list),
        "total_sent": sent,
        "total_failed": len(failed_ids),
        "failed_ids": failed_ids,
        "dry_run": False,
        "mock_outbound": mock_outbound,
    }
    _write_report(out_dir / f"campaign_report_{slug}.json", report)
    return report

def _parse_args(argv=None):
    env_mock = os.environ.get("MOCK_OUTBOUND", "true").strip().lower() != "false"

    parser = argparse.ArgumentParser(description="Run monthly EWS resource campaign.")
    parser.add_argument("--predictions", default="outputs/model_predictions.csv")
    parser.add_argument("--subscribers", default="data/subscribers.csv")
    parser.add_argument("--month", required=True, help="Forecast month as YYYY-MM")
    parser.add_argument("--top-n", type=int, default=50)
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--mock", action=argparse.BooleanOptionalAction, default=env_mock)
    parser.add_argument("--sendgrid-api-key", default=None)
    parser.add_argument("--lob-api-key", default=None)
    return parser.parse_args(argv)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = _parse_args()

    sendgrid_key = args.sendgrid_api_key
    lob_key = args.lob_api_key
    if not args.dry_run and not args.mock:
        sendgrid_key = sendgrid_key or os.environ.get("SENDGRID_API_KEY")
        lob_key = lob_key or os.environ.get("LOB_API_KEY")
        if not sendgrid_key or not lob_key:
            raise SystemExit(
                "Live sends need SENDGRID_API_KEY and LOB_API_KEY in the environment, "
                "or --sendgrid-api-key and --lob-api-key on the command line."
            )

    result = run_monthly_campaign(
        args.predictions,
        args.subscribers,
        args.month,
        top_n=args.top_n,
        dry_run=args.dry_run,
        mock_outbound=args.mock,
        sendgrid_api_key=sendgrid_key,
        lob_api_key=lob_key,
    )

    if result["dry_run"]:
        print(
            f"Dry run for {result['forecast_month']}: "
            f"{result['total_eligible_subscribers']} subscribers across "
            f"{len(result['target_tracts'])} tracts."
        )
    else:
        print(
            f"Campaign for {result['forecast_month']}: "
            f"{result['total_sent']} sent, {result['total_failed']} failed "
            f"(mock_outbound={result['mock_outbound']})."
        )
