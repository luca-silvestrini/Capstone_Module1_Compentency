"""Consumes `transfer.created` v1 events and builds download-notification emails."""
from __future__ import annotations

from shared.contracts import load, validate

CONTRACT = load("transfer.created", 1)
BASE_URL = "https://transfer.digiclips.example/d/"


class BadEvent(ValueError):
    pass


def build_emails(event: dict) -> list[dict]:
    errors = validate(event, CONTRACT)
    if errors:
        raise BadEvent("; ".join(errors))
    mb = event["total_bytes"] / 1024**2
    body = (f"{event['sender_email']} sent you {event['file_count']} file(s) ({mb:.1f} MB).\n"
            f"Download: {BASE_URL}{event['transfer_id']}\n"
            f"Link expires {event['expires_at'][:10]}.")
    if event.get("message"):
        body += f"\n\nMessage: {event['message']}"
    # Unknown extra fields (e.g. 'resumable') are ignored: tolerant reader.
    return [{"to": r, "subject": "You have files waiting on DigiClips", "body": body}
            for r in event["recipient_emails"]]
