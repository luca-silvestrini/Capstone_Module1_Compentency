# DigiClips Scale Lab

A scaled-down, **original** practice repo that applies large-scale software development
practices to the domain of my capstone (DigiClips Media Transfer: a WeTransfer-style
platform where subscribers upload files and recipients get an email download link).

It is intentionally small in code but "large" in process:

| Practice | Where it lives |
|---|---|
| Monorepo with clear package boundaries | `packages/shared`, `packages/transfer_api`, `packages/notifier` |
| Dependency graph + **affected-only CI** | `tools/affected.py`, `packages.json` |
| Versioned **event contract** between services | `contracts/transfer_created.v1.json`, contract tests |
| **Feature flags** with percentage rollout | `packages/shared/src/shared/flags.py`, `flags.json` |
| Code ownership + required reviews | `.github/CODEOWNERS`, `.github/pull_request_template.md` |
| CI pipeline (lint → affected tests → contract check) | `.github/workflows/ci.yml` |
| Architecture boundary enforcement | `tools/check_boundaries.py` |

## Run it

```bash
pip install pytest
python tools/check_boundaries.py
python tools/affected.py packages/shared/src/shared/flags.py   # which packages must be retested?
python tools/run_affected.py packages/shared/src/shared/flags.py
python -m pytest
```
