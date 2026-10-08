# RULForge

Explainable predictive-maintenance platform built on NASA C-MAPSS turbofan data: predict
Remaining Useful Life (RUL) and degradation stage from sensor sequences, explain the prediction,
and (later) ground recommendations in retrieved engineering knowledge through an agentic workflow
with human approval.

> **Status: Phase 1 in progress (Step 1 of 6 done: data loader + RUL generation with tests).**
> Clean rebuild; nothing is trained or evaluated yet and no results are claimed. See `docs/ROADMAP.md`.

## Principle
ML models produce the numbers. Explainability explains the model. RAG supplies evidence. The LLM
communicates. Agents orchestrate tools. A human approves consequential actions.

## Quick start (Windows PowerShell)
```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python scripts/download_data.py
pytest
```

## Layout
```
configs/      YAML settings (draft values until validated)
data/         raw + processed (gitignored; reproduced by scripts)
docs/         plan, architecture, roadmap, decisions, experiments, old-work audit
notebooks/    exploration only; logic is imported from src
scripts/      command-line entry points (download, train, evaluate)
src/rulforge/ data, features, models, training, evaluation, explainability, inference
tests/        pytest; synthetic fixtures, no downloads needed
artifacts/    saved models/scalers (gitignored)
reports/      figures and metric tables
```
RAG, agents, API, frontend, Docker and infrastructure folders are added when their phase starts.
