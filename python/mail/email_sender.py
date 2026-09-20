from pathlib import Path
from datetime import datetime
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from . import OUTPUTS_DIR, append_jsonl, month_label
from .subscribers import Subscriber

TEMPLATES_DIR = Path(__file__).parent / "templates"
FROM_ADDRESS = "ohs-notices@phila.gov"
UNSUBSCRIBE_URL = "https://www.phila.gov/ews/unsubscribe?sid={subscriber_id}"

RESOURCES = {
    "deploy canvassers": [
        "An outreach worker will be in your area this month and can help you apply for rental assistance in person.",
        "Emergency Rental Assistance covers back rent and utilities for households behind on payments.",
        "The Tenant Hotline (215-523-9500) answers questions about your lease at no cost.",
    ],
    "direct mail": [
        "Emergency Rental Assistance covers back rent and utilities for households behind on payments.",
        "A housing counselor can review your lease and budget with you for free.",
        "The Tenant Hotline (215-523-9500) answers questions about your lease at no cost.",
    ],
    "legal aid pop-up": [
        "A free legal clinic is scheduled in your neighborhood this month.",
        "Philadelphia's Right to Counsel program provides a lawyer at no cost if you have an eviction hearing.",
        "The Tenant Hotline (215-523-9500) answers questions about your lease at no cost.",
    ],
    "monitor": [
        "Emergency Rental Assistance covers back rent and utilities for households behind on payments.",
        "The Tenant Hotline (215-523-9500) answers questions about your lease at no cost.",
    ],
}

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)

def resources_for_tier(action_tier: str) -> list[str]:
    return RESOURCES.get(action_tier.strip().lower(), RESOURCES["monitor"])

def subject_line(forecast_month: str) -> str:
    return f"Housing resource alert for your neighborhood: {month_label(forecast_month)}"

def render_email(subscriber: Subscriber, action_tier: str, forecast_month: str) -> str:
    return _env.get_template("email.html").render(
        subject=subject_line(forecast_month),
        first_name=subscriber.first_name,
        month_label=month_label(forecast_month),
        resources=resources_for_tier(action_tier),
        unsubscribe_url=UNSUBSCRIBE_URL.format(subscriber_id=subscriber.subscriber_id),
    )

def _send_via_sendgrid(to_address: str, subject: str, html: str, api_key: str) -> bool:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=FROM_ADDRESS,
        to_emails=to_address,
        subject=subject,
        html_content=html,
    )
    response = SendGridAPIClient(api_key).send(message)
    return 200 <= response.status_code < 300

def send_notification(
    subscriber: Subscriber,
    action_tier: str,
    predicted_filings: int,
    forecast_month: str,
    api_key: Optional[str] = None,
    mock: bool = True,
    output_dir: Optional[Path] = None,
) -> bool:
    # predicted_filings is accepted for auditing but never reaches the resident.
    html = render_email(subscriber, action_tier, forecast_month)

    if mock:
        append_jsonl(
            Path(output_dir or OUTPUTS_DIR) / "mock_email_log.json",
            {
                "timestamp": datetime.now().isoformat(),
                "subscriber_id": subscriber.subscriber_id,
                "to": subscriber.email,
                "action_tier": action_tier,
                "forecast_month": forecast_month,
                "status": "mocked_success",
            },
        )
        print(f"[MOCK] Would send email to {subscriber.email}.")
        return True

    if not api_key:
        raise ValueError("SendGrid API key is required when mock=False.")
    return _send_via_sendgrid(subscriber.email, subject_line(forecast_month), html, api_key)
