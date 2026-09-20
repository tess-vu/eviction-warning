from pathlib import Path
from datetime import datetime
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from . import OUTPUTS_DIR, append_jsonl, month_label
from .email_sender import resources_for_tier
from .subscribers import Subscriber

TEMPLATES_DIR = Path(__file__).parent / "templates"

RETURN_ADDRESS = {
    "name": "Office of Homeless Services",
    "address_line1": "1401 John F. Kennedy Blvd",
    "address_city": "Philadelphia",
    "address_state": "PA",
    "address_zip": "19102",
}

TENANT_RIGHTS = [
    "Your landlord cannot lock you out or shut off utilities without a court order.",
    "You must receive written notice before an eviction case can be filed against you.",
    "You have the right to a habitable home, including working heat and plumbing.",
    "If you face an eviction hearing, you may qualify for a free lawyer through Right to Counsel.",
]

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)

def render_letter(subscriber: Subscriber, action_tier: str, forecast_month: str) -> str:
    letter_date = datetime.strptime(forecast_month, "%Y-%m").strftime("%B 1, %Y")
    return _env.get_template("letter.html").render(
        letter_date=letter_date,
        month_label=month_label(forecast_month),
        subscriber=subscriber,
        resources=resources_for_tier(action_tier),
        tenant_rights=TENANT_RIGHTS,
    )

def _send_via_lob(subscriber: Subscriber, html: str, forecast_month: str, api_key: str) -> str:
    import lob

    lob.api_key = api_key
    letter = lob.Letter.create(
        description=f"EWS resource notice {forecast_month}.",
        to_address={
            "name": subscriber.full_name,
            "address_line1": subscriber.address_line1,
            "address_line2": subscriber.address_line2 or "",
            "address_city": subscriber.city,
            "address_state": subscriber.state,
            "address_zip": subscriber.zip_code,
        },
        from_address=RETURN_ADDRESS,
        file=html,
        color=False,
    )
    return letter["id"]

def send_letter(
    subscriber: Subscriber,
    action_tier: str,
    forecast_month: str,
    api_key: Optional[str] = None,
    mock: bool = True,
    output_dir: Optional[Path] = None,
) -> str:
    html = render_letter(subscriber, action_tier, forecast_month)

    if mock:
        mock_id = f"mock_ltr_{subscriber.subscriber_id[:8]}"
        append_jsonl(
            Path(output_dir or OUTPUTS_DIR) / "mock_mail_log.json",
            {
                "timestamp": datetime.now().isoformat(),
                "subscriber_id": subscriber.subscriber_id,
                "address": f"{subscriber.address_line1}, {subscriber.city}, {subscriber.zip_code}",
                "action_tier": action_tier,
                "forecast_month": forecast_month,
                "mock_letter_id": mock_id,
                "status": "mocked_success",
            },
        )
        print(f"[MOCK] Would send letter to {subscriber.full_name} at {subscriber.address_line1}.")
        return mock_id

    if not api_key:
        raise ValueError("Lob API key is required when mock=False.")
    return _send_via_lob(subscriber, html, forecast_month, api_key)
