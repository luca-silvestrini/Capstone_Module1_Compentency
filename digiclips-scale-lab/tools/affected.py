#!/usr/bin/env python3
"""Given changed file paths, print which packages must be rebuilt/retested.

A change to a package affects that package and everything that (transitively)
depends on it. Changes to contracts/ affect every package that uses them, and
changes to repo-wide config affect everything. This is the idea behind
"affected" builds in large monorepos (Bazel, Nx, Turborepo), reduced to ~40 lines.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOBAL_FILES = {"packages.json", ".github/workflows/ci.yml", "pyproject.toml"}


def load_graph() -> dict:
    return json.loads((ROOT / "packages.json").read_text())


def reverse_deps(graph: dict) -> dict[str, set[str]]:
    rev = {name: set() for name in graph}
    for name, info in graph.items():
        for dep in info["depends_on"]:
            rev[dep].add(name)
    return rev


def affected(changed: list[str], graph: dict | None = None) -> list[str]:
    graph = graph or load_graph()
    rev = reverse_deps(graph)
    hit: set[str] = set()
    for path in changed:
        path = path.replace("\\", "/")
        if path in GLOBAL_FILES:
            return sorted(graph)
        if path.startswith("contracts/"):
            hit |= set(graph)  # every service that speaks the event contract
            continue
        for name, info in graph.items():
            if path.startswith(info["path"] + "/"):
                hit.add(name)
    queue = list(hit)
    while queue:  # walk dependents transitively
        for dependent in rev[queue.pop()]:
            if dependent not in hit:
                hit.add(dependent)
                queue.append(dependent)
    return sorted(hit)


if __name__ == "__main__":
    result = affected(sys.argv[1:])
    print(" ".join(result) if result else "(nothing affected)")
