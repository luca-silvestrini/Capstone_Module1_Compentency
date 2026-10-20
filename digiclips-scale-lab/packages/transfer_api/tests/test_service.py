import pytest

from shared.contracts import load, validate
from shared.flags import Flag, FlagStore
from transfer_api.service import TransferError, create_transfer

FLAGS = FlagStore({
    "expiring_links_v2": Flag("expiring_links_v2", True, 100),
    "resumable_uploads": Flag("resumable_uploads", True, 0, ("admin",)),
})


def test_producer_event_matches_contract_v1():
    ev = create_transfer("a@x.com", ["b@y.com"], [("clip.mp4", 1000)], FLAGS, message="hi")
    assert validate(ev, load("transfer.created", 1)) == []


def test_size_limit_applies_to_subscribers_not_admins():
    big = [("raw.mov", 3 * 1024**3)]
    with pytest.raises(TransferError):
        create_transfer("a@x.com", ["b@y.com"], big, FLAGS)
    assert create_transfer("a@x.com", ["b@y.com"], big, FLAGS, role="admin")["resumable"] is True


def test_requires_recipient_and_file():
    with pytest.raises(TransferError):
        create_transfer("a@x.com", [], [("f", 1)], FLAGS)
    with pytest.raises(TransferError):
        create_transfer("a@x.com", ["b@y.com"], [], FLAGS)
