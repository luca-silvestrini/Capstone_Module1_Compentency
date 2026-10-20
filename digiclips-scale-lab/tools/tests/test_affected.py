import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from affected import affected  # noqa: E402


def test_leaf_change_only_affects_itself():
    assert affected(["packages/notifier/src/notifier/handler.py"]) == ["notifier"]


def test_shared_change_ripples_to_dependents():
    assert affected(["packages/shared/src/shared/flags.py"]) == ["notifier", "shared", "transfer_api"]


def test_contract_change_affects_all_and_global_config_affects_all():
    assert affected(["contracts/transfer_created.v1.json"]) == ["notifier", "shared", "transfer_api"]
    assert affected(["packages.json"]) == ["notifier", "shared", "transfer_api"]


def test_docs_change_affects_nothing():
    assert affected(["README.md"]) == []
