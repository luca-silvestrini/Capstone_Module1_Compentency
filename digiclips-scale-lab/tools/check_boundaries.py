#!/usr/bin/env python3
"""Fail if a package imports another package it hasn't declared in packages.json.

On big teams, architecture erodes one convenient import at a time. This check
makes the dependency graph in packages.json the source of truth: e.g. notifier
may import shared, but must never import transfer_api directly.
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
graph = json.loads((ROOT / "packages.json").read_text())
violations = []
for name, info in graph.items():
    allowed = set(info["depends_on"]) | {name}
    for py in (ROOT / info["path"] / "src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                mods = [node.module]
            for m in mods:
                top = m.split(".")[0]
                if top in graph and top not in allowed:
                    violations.append(f"{py.relative_to(ROOT)}:{node.lineno} imports '{top}' (not declared)")
for v in violations:
    print("BOUNDARY VIOLATION:", v)
print(f"checked {len(graph)} packages: {'FAIL' if violations else 'OK'} ({len(violations)} violations)")
sys.exit(1 if violations else 0)
