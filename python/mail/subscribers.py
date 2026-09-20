import csv
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
VALID_CHANNELS = {"email", "mail", "both"}
TRUTHY = {"true", "t", "yes", "y", "1"}

REQUIRED_COLUMNS = {
    "subscriber_id", "email", "full_name", "address_line1", "address_line2",
    "city", "state", "zip_code", "GEOID", "channel", "opted_in_at", "active",
}

@dataclass
class Subscriber:
    subscriber_id: str
    email: Optional[str]
    full_name: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    zip_code: str
    GEOID: str
    channel: str
    opted_in_at: datetime
    active: bool

    @property
    def first_name(self) -> str:
        parts = self.full_name.split()
        return parts[0] if parts else "neighbor"

    @property
    def wants_email(self) -> bool:
        return self.channel in ("email", "both")

    @property
    def wants_mail(self) -> bool:
        return self.channel in ("mail", "both")

def _to_subscriber(row: dict) -> Subscriber:
    return Subscriber(
        subscriber_id=row["subscriber_id"].strip(),
        email=(row["email"] or "").strip() or None,
        full_name=row["full_name"].strip(),
        address_line1=row["address_line1"].strip(),
        address_line2=(row["address_line2"] or "").strip() or None,
        city=row["city"].strip(),
        state=row["state"].strip(),
        zip_code=row["zip_code"].strip(),
        GEOID=row["GEOID"].strip(),
        channel=row["channel"].strip().lower(),
        opted_in_at=datetime.fromisoformat(row["opted_in_at"].strip()),
        active=row["active"].strip().lower() in TRUTHY,
    )

def load_subscribers(path: str) -> list[Subscriber]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        return [_to_subscriber(row) for row in reader]

def get_subscribers_for_tracts(
    subscribers: Iterable[Subscriber], geoid_list: Iterable[str]
) -> list[Subscriber]:
    targets = set(geoid_list)
    return [s for s in subscribers if s.active and s.GEOID in targets]

def validate_subscriber_list(subscribers: Iterable[Subscriber]) -> list[str]:
    errors = []
    seen = set()

    for s in subscribers:
        label = s.subscriber_id or "<no id>"

        if not s.subscriber_id:
            errors.append("A row has no subscriber_id.")
        elif s.subscriber_id in seen:
            errors.append(f"{label}: duplicate subscriber_id.")
        seen.add(s.subscriber_id)

        if not s.full_name:
            errors.append(f"{label}: full_name is empty.")
        if s.channel not in VALID_CHANNELS:
            errors.append(
                f"{label}: channel {s.channel!r} is not one of {sorted(VALID_CHANNELS)}."
            )
        if s.wants_email and not s.email:
            errors.append(f"{label}: subscribed to email but no address is on file.")
        if s.email and not EMAIL_PATTERN.match(s.email):
            errors.append(f"{label}: {s.email!r} is not a usable email address.")
        if s.wants_mail and not (s.address_line1 and s.zip_code):
            errors.append(f"{label}: subscribed to mail but postal address is incomplete.")

    return errors
