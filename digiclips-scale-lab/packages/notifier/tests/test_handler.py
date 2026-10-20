import pytest

from notifier.handler import BadEvent, build_emails

GOOD = {
    "transfer_id": "t-1", "sender_email": "a@x.com", "recipient_emails": ["b@y.com", "c@z.com"],
    "file_count": 2, "total_bytes": 5 * 1024**2, "expires_at": "2026-11-03T00:00:00+00:00",
    "resumable": False,  # field the consumer doesn't know about yet
}


def test_one_email_per_recipient_and_ignores_unknown_fields():
    emails = build_emails(GOOD)
    assert [e["to"] for e in emails] == ["b@y.com", "c@z.com"]
    assert "5.0 MB" in emails[0]["body"] and "t-1" in emails[0]["body"]


def test_rejects_events_that_break_the_contract():
    bad = {k: v for k, v in GOOD.items() if k != "expires_at"}
    with pytest.raises(BadEvent, match="expires_at"):
        build_emails(bad)
