"""Tiny schema validator for versioned events shared between services."""
from __future__ import annotations

import json
from pathlib import Path

_TYPES = {"str": str, "int": int, "list": list, "dict": dict, "bool": bool}
CONTRACT_DIR = Path(__file__).resolve().parents[4] / "contracts"


def load(name: str, version: int) -> dict:
    return json.loads((CONTRACT_DIR / f"{name.replace('.', '_')}.v{version}.json").read_text())


def validate(event: dict, contract: dict) -> list[str]:
    errors = []
    for key, typ in contract["required"].items():
        if key not in event:
            errors.append(f"missing required field '{key}'")
        elif not isinstance(event[key], _TYPES[typ]):
            errors.append(f"field '{key}' should be {typ}")
    for key, typ in contract.get("optional", {}).items():
        if key in event and not isinstance(event[key], _TYPES[typ]):
            errors.append(f"field '{key}' should be {typ}")
    return errors
