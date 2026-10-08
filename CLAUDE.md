# CLAUDE.md - RULForge

Explainable predictive-maintenance platform on NASA C-MAPSS. Read `docs/PROJECT_PLAN.md`,
`docs/ROADMAP.md`, `docs/DECISIONS.md` and `docs/OLD_NOTEBOOKS_AUDIT.md` first.

## Working agreement (owner's rules, set 2026-10-08)
- **Ask first.** Propose each action and wait for the owner's approval before creating, changing, deleting or running
  anything. Do not start the next step on your own.
- **Diary.** After every step, add an entry to `docs/DIARY.md` (what we did, why, what we found, decision, what to
  learn). Refresh the copy in the RUL Forge project at the end of each step.
- **ML-engineer loop on Colab:** write the question and metric first -> run with a fixed seed -> log the result ->
  compare every model on the same split and metrics over several seeds -> choose the best model on VALIDATION data only
  -> record the decision and why. Touch the test set once, at the end.
- **Notebook style:** write core ML code in the notebook first so every line is visible and understood, then promote it
  to tested modules in `src/rulforge/` once stable. Colab clones the GitHub repo in its first cell.

## Master instructions (full text: `docs/WORKING_INSTRUCTIONS.md`)
The owner's 31-section operating rules apply. Condensed (the file wins if anything here is unclear):
- Act as senior ML engineer + mentor, not a code generator. Flag weak approaches BEFORE implementing, using
  PROBLEM / WHY IT MATTERS / RECOMMENDED APPROACH / TRADE-OFF / ACTION. Do not agree just because it was requested.
- Simplest approach that meets the goal; baselines first; no technology added without a stated reason (no FOMO).
- Treat ML as experiments: question -> hypothesis -> baseline -> design -> result -> analysis -> decision -> next.
  Change one major variable at a time; check leakage/overfitting/seed sensitivity; investigate results that look too
  good or too bad; analyse before changing the model.
- Fair comparison tables (model, data, features, split, hyperparameters, metrics, cost, params, time, limitations);
  never one metric alone; do error analysis (worst/best engines, stages), not only aggregates.
- Teach genuinely new concepts briefly (CONCEPT / WHY / HOW / FIT / TRADE-OFFS / MINIMUM TO KNOW) before or while
  implementing; don't over-teach routine steps. Max 4 learning resources (verified links only, else say unverified).
- Notebook order: objective, problem, imports, config, data, validation, EDA, preprocessing, features, dataset,
  model, training, validation, evaluation, plots, error analysis, results, conclusions, next steps.
- Reproducibility: seeds, recorded hyperparameters/config, saved metrics and plots. Security: no hard-coded secrets.
- Integrity: never fabricate results, citations, links; label EXPECTED / ASSUMED / UNVERIFIED.
- Document major decisions in `docs/DECISIONS.md`. "review the project" triggers the severity-graded review (sec. 29).
- End significant tasks with COMPLETED / DECISION / NEXT STEP / WATCH OUT / OPTIONAL IMPROVEMENT; keep it short.
- Model escalation (sec. 8): only note MODEL ESCALATION for genuinely hard reasoning, never just for length.
- **Resolved conflict:** sections 25-26 say "assume and proceed"; the owner chose (2026-10-08) **ask before acting,
  assume freely only in explanations**. The ask-first rule above overrides sections 25-26.

## Core principles
1. ML models make the numerical RUL / stage predictions; LLMs never replace them.
2. RAG supplies evidence; agents orchestrate tools; a human approves consequential actions.
3. Every important result must be reproducible from (config, seed).
4. Never fabricate metrics or claim unimplemented capabilities.

## Current state
Clean rebuild. Done: folder structure, draft configs, data loader + RUL generation (`src/rulforge/data/`)
with tests. **No features, models or results yet.** The old Colab work is archived as PDFs in `docs/legacy/` and its metrics are INVALID
(test RUL labels were joined by position, so every engine got the next engine's RUL).

## Current phase
Phase 1: reproducible ML foundation. FD001 is primary; FD002 is one extra benchmark afterwards; FD003/FD004 are out of scope (D-002); the subset is a config value.
Order: baselines ->
XGBoost -> LSTM -> Attention-LSTM, seed ensembles for uncertainty, SHAP + attention/IG.

## ML correctness rules (non-negotiable)
- RUL per engine; join the test RUL file by ENGINE ID; add a test that FD001 engines 1/2/3 end at 112/98/69.
- Split by engine (train/validation); early stopping and model selection on validation ONLY.
- Fit scalers/feature selection on training engines only; rolling/lag features per engine, backward-looking.
- Windows never cross engine boundaries.
- Report official last-cycle-per-engine test metrics plus validation metrics; several seeds, mean +/- spread, no best-run picking.
- Stage thresholds are fixed and justified before any model runs; report a majority-class baseline, macro-F1, confusion matrix.
- Attention weights are not causal proof. Do not invent sensor meanings; use NASA documentation.

## Workflow for every change
1. State the problem. 2. Inspect existing code. 3. Smallest coherent change. 4. Implement.
5. Add/update tests. 6. Run them. 7. Report what changed, what passed, what is uncertain.
8. Update docs/ROADMAP.md, DECISIONS.md or EXPERIMENTS.md if project state changed.

## Do not
Rewrite working code without evidence; start RAG/agents/AWS before the ML foundation is reproducible;
add dependencies without justification; commit secrets or data; add AWS services for keywords.

## Learning mode
The owner is learning AI engineering through this project. Explain the concept behind each
component, explain unfamiliar abstractions, and prefer teaching "why" over only giving code.
