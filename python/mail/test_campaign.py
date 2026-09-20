import json
import sys
from unittest.mock import MagicMock
import numpy as np
import pandas as pd
import pytest
from python.mail import direct_mail, email_sender
from python.mail.campaign import run_monthly_campaign
from python.mail.subscribers import (
    load_subscribers,
    get_subscribers_for_tracts,
    validate_subscriber_list,
)

CRITICAL = ["42101000100", "42101000200", "42101000300"]
QUIET = "42101009900"

def _write_predictions(tmp_path):
    rng = np.random.default_rng(7)
    geoids = CRITICAL + [QUIET] + [f"4210100{i:04d}" for i in range(20)]
    predicted = [18.4, 16.2, 13.8, 4.1] + list(rng.uniform(0, 11.5, size=20))

    df = pd.DataFrame({
        "GEOID": geoids,
        "date": "2026-01-01",
        "neighborhood": "Kensington",
        "racial_majority": "Hispanic",
        "filings_count": [int(p) for p in predicted],
        "predicted": predicted,
    })
    path = tmp_path / "preds.csv"
    df.to_csv(path, index=False)
    return str(path)

def _write_subscribers(tmp_path, rows=None):
    header = (
        "subscriber_id,email,full_name,address_line1,address_line2,city,state,"
        "zip_code,GEOID,channel,opted_in_at,active"
    )
    rows = rows if rows is not None else [
        f"SUB0001,a@example.com,Rosa Alvarez,1 Main St,,Philadelphia,PA,19133,{CRITICAL[0]},email,2025-11-04T09:12:00,true",
        f"SUB0002,,Darnell Whitaker,2 Main St,,Philadelphia,PA,19146,{CRITICAL[1]},mail,2025-11-06T14:40:00,true",
        f"SUB0003,c@example.com,Minh Tran,3 Main St,,Philadelphia,PA,19138,{CRITICAL[2]},both,2025-12-01T08:05:00,true",
        f"SUB0004,d@example.com,Joy Okafor,4 Main St,,Philadelphia,PA,19124,{CRITICAL[0]},email,2025-10-19T17:22:00,false",
        f"SUB0005,e@example.com,Pat Brennan,5 Main St,,Philadelphia,PA,19134,{QUIET},both,2026-01-08T11:30:00,true",
    ]
    path = tmp_path / "subs.csv"
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return str(path)

@pytest.fixture
def campaign_args(tmp_path):
    return {
        "predictions_path": _write_predictions(tmp_path),
        "subscribers_path": _write_subscribers(tmp_path),
        "forecast_month": "2026-01",
        "output_dir": tmp_path,
    }

@pytest.fixture
def fake_sdks(monkeypatch):
    sendgrid = MagicMock()
    sendgrid.SendGridAPIClient.return_value.send.return_value.status_code = 202
    lob = MagicMock()
    lob.Letter.create.return_value = {"id": "ltr_abc123"}

    modules = {
        "sendgrid": sendgrid,
        "sendgrid.helpers": MagicMock(),
        "sendgrid.helpers.mail": MagicMock(),
        "lob": lob,
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    return sendgrid, lob

def test_dry_run_reports_without_touching_senders(campaign_args, tmp_path, monkeypatch):
    email_spy = MagicMock()
    mail_spy = MagicMock()
    monkeypatch.setattr(email_sender, "send_notification", email_spy)
    monkeypatch.setattr(direct_mail, "send_letter", mail_spy)

    report = run_monthly_campaign(**campaign_args, dry_run=True)

    email_spy.assert_not_called()
    mail_spy.assert_not_called()
    assert report["dry_run"] is True
    assert report["total_eligible_subscribers"] == 3
    assert report["subscribers_by_channel"] == {"email": 1, "mail": 1, "both": 1}
    assert sorted(report["target_tracts"]) == sorted(CRITICAL)

    written = json.loads((tmp_path / "campaign_dry_run_2026_01.json").read_text())
    assert written == report
    assert not (tmp_path / "mock_email_log.json").exists()
    assert not (tmp_path / "mock_mail_log.json").exists()

def test_inactive_and_out_of_scope_subscribers_excluded(campaign_args):
    report = run_monthly_campaign(**campaign_args, dry_run=True)
    assert report["total_eligible_subscribers"] == 3

    subscribers = load_subscribers(campaign_args["subscribers_path"])
    selected = {s.subscriber_id for s in get_subscribers_for_tracts(subscribers, CRITICAL)}
    assert "SUB0004" not in selected
    assert "SUB0005" not in selected

def test_mock_send_writes_logs_and_report(campaign_args, tmp_path, monkeypatch):
    email_spy = MagicMock(wraps=email_sender.send_notification)
    mail_spy = MagicMock(wraps=direct_mail.send_letter)
    monkeypatch.setattr(email_sender, "send_notification", email_spy)
    monkeypatch.setattr(direct_mail, "send_letter", mail_spy)

    report = run_monthly_campaign(**campaign_args, dry_run=False, mock_outbound=True)

    assert email_spy.call_count == 2
    assert mail_spy.call_count == 2
    assert all(call.kwargs["mock"] is True for call in email_spy.call_args_list)
    assert all(call.kwargs["mock"] is True for call in mail_spy.call_args_list)

    assert report["total_targeted"] == 3
    assert report["total_sent"] == 3
    assert report["total_failed"] == 0
    assert report["failed_ids"] == []
    assert report["mock_outbound"] is True

    email_log = (tmp_path / "mock_email_log.json").read_text().strip().splitlines()
    mail_log = (tmp_path / "mock_mail_log.json").read_text().strip().splitlines()
    assert len(email_log) == 2
    assert len(mail_log) == 2
    assert json.loads(email_log[0])["status"] == "mocked_success"

def test_report_has_required_keys(campaign_args, tmp_path):
    run_monthly_campaign(**campaign_args, dry_run=False, mock_outbound=True)
    written = json.loads((tmp_path / "campaign_report_2026_01.json").read_text())
    expected = {
        "forecast_month", "total_targeted", "total_sent",
        "total_failed", "failed_ids", "dry_run", "mock_outbound",
    }
    assert expected <= set(written)

def test_live_send_without_keys_raises_before_any_send(campaign_args, monkeypatch):
    email_spy = MagicMock()
    monkeypatch.setattr(email_sender, "send_notification", email_spy)

    with pytest.raises(ValueError, match="SendGrid"):
        run_monthly_campaign(**campaign_args, dry_run=False, mock_outbound=False)
    email_spy.assert_not_called()

def test_live_send_calls_sdks(campaign_args, fake_sdks):
    sendgrid, lob = fake_sdks
    report = run_monthly_campaign(
        **campaign_args,
        dry_run=False,
        mock_outbound=False,
        sendgrid_api_key="SG.test",
        lob_api_key="test_key",
    )

    assert sendgrid.SendGridAPIClient.call_count == 2
    assert lob.Letter.create.call_count == 2
    assert lob.api_key == "test_key"
    assert report["total_sent"] == 3
    assert report["mock_outbound"] is False

def test_send_failure_is_recorded_without_aborting(campaign_args, monkeypatch):
    def flaky(subscriber, *args, **kwargs):
        if subscriber.subscriber_id == "SUB0001":
            raise RuntimeError("SendGrid rejected the message")
        return True

    monkeypatch.setattr(email_sender, "send_notification", flaky)
    report = run_monthly_campaign(**campaign_args, dry_run=False, mock_outbound=True)

    assert report["failed_ids"] == ["SUB0001"]
    assert report["total_failed"] == 1
    assert report["total_sent"] == 2

def test_live_send_blocked_when_nobody_opted_in(tmp_path, campaign_args):
    campaign_args["subscribers_path"] = _write_subscribers(tmp_path, rows=[
        f"SUB0009,z@example.com,Nobody Here,9 Main St,,Philadelphia,PA,19134,{QUIET},email,2026-01-08T11:30:00,true",
    ])
    with pytest.raises(ValueError, match="opted in"):
        run_monthly_campaign(**campaign_args, dry_run=False, mock_outbound=True)

def test_validate_flags_bad_rows(tmp_path):
    path = _write_subscribers(tmp_path, rows=[
        f"SUB0001,not-an-email,Rosa Alvarez,1 Main St,,Philadelphia,PA,19133,{CRITICAL[0]},email,2025-11-04T09:12:00,true",
        f"SUB0002,,Darnell Whitaker,,,Philadelphia,PA,,{CRITICAL[1]},mail,2025-11-06T14:40:00,true",
        f"SUB0002,c@example.com,Minh Tran,3 Main St,,Philadelphia,PA,19138,{CRITICAL[2]},carrier-pigeon,2025-12-01T08:05:00,true",
    ])
    errors = validate_subscriber_list(load_subscribers(path))
    joined = " ".join(errors)
    assert "not a usable email address" in joined
    assert "postal address is incomplete" in joined
    assert "duplicate subscriber_id" in joined
    assert "carrier-pigeon" in joined
