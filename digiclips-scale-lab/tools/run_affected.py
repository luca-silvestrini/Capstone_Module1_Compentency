#!/usr/bin/env python3
"""Run pytest only for packages affected by the given changed files."""
import subprocess
import sys

from affected import affected, load_graph

changed = sys.argv[1:]
graph = load_graph()
targets = affected(changed, graph)
print(f"changed files : {' '.join(changed) or '(none)'}")
print(f"affected pkgs : {', '.join(targets) or '(none)'}")
skipped = sorted(set(graph) - set(targets))
print(f"skipped pkgs  : {', '.join(skipped) or '(none)'}")
if not targets:
    sys.exit(0)
paths = [graph[t]["path"] + "/tests" for t in targets]
sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q", *paths]))
