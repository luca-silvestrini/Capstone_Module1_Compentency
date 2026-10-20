"""Creates transfers and publishes a `transfer.created` v1 event.

The API never calls the notifier directly; it only emits an event that matches
the shared contract. That keeps the two services independently deployable.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from shared.flags import FlagStore

MAX_FREE_BYTES = 2 * 1024**3  # 2 GB


class TransferError(ValueError):
    pass


def create_transfer(sender: str, recipients: list[str], files: list[tuple[str, int]],
                    flags: FlagStore, role: str = "subscriber", message: str | None = None,
                    now: datetime | None = None) -> dict:
    if not recipients:
        raise TransferError("at least one recipient is required")
    if not files:
        raise TransferError("at least one file is required")
    total = sum(size for _, size in files)
    if total > MAX_FREE_BYTES and role != "admin":
        raise TransferError("transfer exceeds 2 GB limit")

    now = now or datetime.now(timezone.utc)
    days = 14 if flags.is_on("expiring_links_v2", sender, role) else 7
    event = {
        "transfer_id": str(uuid.uuid4()),
        "sender_email": sender,
        "recipient_emails": list(recipients),
        "file_count": len(files),
        "total_bytes": total,
        "expires_at": (now + timedelta(days=days)).isoformat(),
        "resumable": flags.is_on("resumable_uploads", sender, role),
    }
    if message:
        event["message"] = message
    return event
