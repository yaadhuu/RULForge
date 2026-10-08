# Decisions

Format: decision · context · alternatives · why · tradeoffs · date · how to revisit.

## D-001 Single installable package `src/rulforge/`
Context: API, RAG and agents all need the same model/preprocessing code. Alternatives: separate top-level
`api/ rag/ agents/` folders. Why: one import path, one Docker image, no cross-folder import mess.
Tradeoff: services are less physically separated. Date: 2026-10-08. Revisit if services need independent deploys.

## D-002 Scope: FD001 is the primary dataset; FD002 is one extra benchmark; FD003/FD004 are out of scope
Context: FD001 (1 flight condition, 1 fault type) is the simplest C-MAPSS subset; FD002 adds 6 flight conditions;
FD003/FD004 add a second fault type (fan degradation). Decision: build everything (ML, API, RAG, agent, demo) on FD001;
after FD001 is finished in Phase 1, run the same pipeline on FD002 as a single generalisation benchmark.
Alternatives: FD001 only (simplest); FD001+FD002 through the whole platform (more work in API/agent/demo, rejected).
Why: FD002 adds one new idea (per-condition sensor normalisation) at modest cost and shows the pipeline is not tuned to
the easiest data; dropping FD003/FD004 avoids a second failure-mode problem the platform does not need.
Tradeoff: no claim about multi-fault-mode data. Date: 2026-10-08.
Revisit: if FD002 results are poor or take too long, fall back to FD001 only; the subset is a config value, so adding
FD003/FD004 later is cheap.

## D-003 Ensemble uncertainty included in Phase 1
Context: the API's confidence field must be justified. Why: seeds are trained anyway; ensemble spread is a
cheap, defensible uncertainty signal. Alternatives: quantile regression, MC dropout (can be added). Date: 2026-10-08.

## D-004 Data and artifacts are not committed
Why: reproducibility via `scripts/download_data.py` and configs; keeps the repo small. Date: 2026-10-08.

## D-005 Old results discarded; clean rebuild
Context: old test RUL labels were misaligned (see OLD_NOTEBOOKS_AUDIT.md); old metrics are invalid.
Date: 2026-10-08.

## Open (decide from evidence, not memory)
RUL cap (100/125/150) · stage classes and thresholds · sequence length · feature set · whether the stage head helps.
