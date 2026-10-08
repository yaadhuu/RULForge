# RULForge Diary

The story of the project in order: what we did, why we did it, what we found, and what it taught us.
Read it top to bottom at the end and you have the whole project, including answers to "why did you do that?".

**How entries are written:** *What we did* · *Why* · *What we found* · *Decision* · *What to learn from it*.
Numbers are only recorded when they came from a run or a check. Old-notebook numbers are marked INVALID.

---

## Working agreement (set 2026-10-08)
- Claude proposes each action and **waits for approval** before creating, changing or running anything.
- Experiments follow the ML-engineer loop on Colab: write the question and metric first -> run with a fixed seed ->
  log the result -> compare every model on the same split and metrics, over several seeds -> **choose the best model on
  validation data only** -> record the decision and why. The test set is used once, at the end.
- Notebooks: core ML code is written in the notebook first so every line is visible and understood, then promoted to
  tested modules in `src/rulforge/` once stable. Colab gets the code by cloning the GitHub repo in the first cell.
- Every step is written into this diary. Why: so the project can be re-read and explained end to end.

---

## Entry 1 - Understanding the project (2026-10-08)
**What we did.** Read the Master Implementation Plan (.docx) and the Project Brief (.md).
**Why.** We are rebuilding RULForge from scratch, so we needed one shared picture of the goal first.
**What we found.**
- RULForge predicts **Remaining Useful Life (RUL)** of jet engines from sensor readings (NASA C-MAPSS), classifies a
  degradation stage, explains the prediction, and later adds RAG, an agent, MLOps and AWS.
- Core rule: **ML makes the numbers; the LLM never replaces the model.** Explainability explains the model, RAG supplies
  evidence, the LLM communicates, agents orchestrate tools, a human approves consequential actions.
- Order matters: data -> ML -> evaluation -> explainability -> engineering -> MLOps -> RAG -> agents -> cloud.
**What to learn from it.** RUL = cycles left before failure. Capping RUL at 125 means early life is treated as "healthy
enough"; the cap is a setting to be tested, not a law. CMAPSS FD001 = 100 train engines run to failure, 100 test engines cut
off early, plus a file with their true remaining life.

## Entry 2 - Auditing the old Colab notebooks (2026-10-08)
**What we did.** Read PDF prints of the five old notebooks (EDA, Attention-LSTM training, XGBoost features, SHAP,
attention analysis) and re-ran the old test-RUL logic on the real FD001 files.
**Why.** The old results were the starting point; we had to know whether to trust them.
**What we found (main result).** The old **test RUL labels were wrong**. The code joined the RUL file to engines by *row
position* (`reset_index(drop=True)` against engine ids 1..100), so every engine got its neighbour's value (engine 1 got 98
instead of 112; engine 100 got nothing, later hidden by `fillna(median)` / `dropna`). All 12,898 labelled test rows were
wrong. **Every old test metric is therefore INVALID** (XGBoost ~43-44 RMSE, Attention-LSTM 43.35 RMSE / 81% accuracy).
Other problems: no validation set (early stopping and "best epoch" chosen on the test set), scoring all test rows instead of
the official last-cycle protocol, stage accuracy (~81%) barely above "always predict healthy" (~80%), nearly flat attention
weights read as "important timesteps", and invented sensor meanings in the SHAP notebook.
**Decision.** Discard old results; clean rebuild. Keep the good parts: the EDA, per-engine rolling features, and the
Attention-LSTM design as a starting config.
**What to learn from it.**
- *Data leakage / label errors:* a model can look fine while being scored against wrong answers. Always test your labels.
- *Validation vs test:* pick models on validation data; the test set is a final exam, taken once.
- *Majority-class baseline:* accuracy means little when one class dominates; use macro-F1 and a confusion matrix.
- *Attention is not an explanation,* and *SHAP shows what the model used, not what caused failure.*
- Never invent sensor meanings; take them from NASA's documentation.
Full write-up: `docs/OLD_NOTEBOOKS_AUDIT.md`.

## Entry 3 - Approach suggestions we agreed on (2026-10-08)
**What we decided.**
- Build for all four CMAPSS subsets but start with FD001 (1 operating condition, 1 fault). Extend to FD002-FD004 later.
- Baselines before deep models: naive, Linear Regression, Random Forest, XGBoost.
- Treat the RUL cap (100/125/150) and stage thresholds as things to decide from evidence.
- Include ensemble uncertainty in Phase 1 (we train several seeds anyway).
- Report the NASA asymmetric score next to RMSE (late predictions are worse than early ones).
- Explain sequence models with Integrated Gradients/SHAP as well as attention.
**Expectation to check later.** From memory of the literature, good FD001 models score roughly 11-18 RMSE on the last
cycle of each test engine. If ours is near 40, suspect a bug. (To be verified against sources.)

## Entry 4 - Project structure (2026-10-08)
**What we did.** Reviewed the proposed repo layout and agreed a revised one.
**Why / changes.** One installable package `src/rulforge/` (training, API and agent share code); an `inference/` module so
training and serving use the same preprocessing; saved models go in `artifacts/` (not `models/`, which clashed with code);
no empty folders for future phases; raw data not committed; tests use tiny synthetic data; experiment tables generated from
run logs, not typed by hand.
**What to learn from it.** Training/serving skew (preprocessing that differs between training and production) is a classic
ML bug; one shared predict path prevents it.

## Entry 5 - Creating the project in `Z:\RULForge` (2026-10-08)
**What we did.** Created the folder tree, draft configs, docs, a data-download script and a smoke test; archived the old
notebooks in `docs/legacy/`. Tested the download script (it checks row counts against the official FD001-FD004 sizes).
**Caveat.** Two files (`ci.yml`, `.pre-commit-config.yaml`) are protected paths, so they were saved as `.txt` in
`docs/setup_files/` for you to rename.
**Open:** confirm `pip install -e ".[dev]"`, the download script and `pytest` on your own machine.

## Entry 6 - Step 1: data loader and RUL generation (2026-10-08)
**What we did.** Wrote `data/load.py` (reads and validates files), `data/rul.py` (train/test RUL with an optional cap),
`config.py`, and 13 tests.
**Why.** RUL is the target everything else learns from; a wrong target ruins every later result. This is also the exact place
the old project broke.
**How it works.**
- Train: `RUL = last_cycle - cycle` per engine.
- Test: `RUL = rul_after_last + (last_cycle - cycle)`, with `rul_after_last` looked up **by engine id** (`Series.map`),
  which cannot shift. `rul_raw` keeps the true value; `rul` is the capped training target.
**How we know it is right.** 13 tests pass on the real FD001 data (engines 1/2/3 end at RUL 112/98/69; 20,631/13,096/100
rows). We also re-introduced the old bug on purpose: two tests failed (engine 1 came out as 98). Restoring the fix made all
13 pass. A test that has never failed has not proven anything; this one has.
**What to learn from it.** Label/index alignment in pandas: joining by position vs by label. Writing a test that would have
caught a real past bug (a regression test) and checking it by breaking the code on purpose (a mutation check).
**Open:** run the tests on your machine.

## Entry 7 - Prior work, what FD001-FD004 are, and our dataset scope (2026-10-08)
**What we did.** Looked up the dataset paper, published benchmark results and related projects; counted engines in the
downloaded files; decided the dataset scope.
**Why.** Before building, we wanted to know what the data really is, what good results look like, and whether anyone
already combined RUL models with RAG/LLMs.
**What we found.**
- *Dataset paper:* Saxena, Goebel, Simon, Eklund (2008, NASA PHM08 challenge). Data comes from the C-MAPSS turbofan
  simulator: compressor (HPC) wear follows an exponential path with random parameters until a health index hits zero,
  under six flight conditions, with process and measurement noise. It lists the 21 sensors (T2, T24, T30, T50, P2, P15,
  P30, Nf, Nc, epr, Ps30, phi, NRf, NRc, BPR, farB, htBleed, Nf_dmd, PCNfR_dmd, W31, W32). It does not describe the
  FD001-FD004 split; that comes from NASA's data readme and later papers.
- *The four subsets* (engine counts verified from the files; conditions/faults from published tables):
  FD001 100/100 engines, 1 condition, 1 fault (HPC) · FD002 260/259, 6 conditions, 1 fault · FD003 100/100, 1 condition,
  2 faults (HPC + fan) · FD004 249/248, 6 conditions, 2 faults.
- **Correction:** earlier we wrote FD004 as 248 train / 249 test. The files show 249 train / 248 test. Fixed in
  `data/README.md`.
- *Published results* (RMSE, as printed in Chaoub et al. 2021 and Akbari Pour et al. 2025): FD001 roughly 11-16.5,
  FD002 roughly 13-20, FD003 roughly 9-13, FD004 roughly 14-22 for the better methods. Examples: DA-TCN 11.78 / 16.95 /
  11.56 / 18.23; PSTFormer 12.08 / 13.00 / 12.11 / 14.38. The FD001 range confirms the earlier "roughly 11-18" estimate;
  our old 43 was far outside it because of the label bug.
- The same method (LSTM) appears with different numbers in different papers, and papers use different RUL caps (125 vs 130)
  and window lengths (19-125). Published tables are NOT directly comparable.
- *Related work:* Dimidov & Frank (PHME 2026) test multimodal LLMs on FD001 RUL; retrieving similar degradation segments
  improves them, with noted limits for practical use. PARAM (2025) uses RAG + LLM for bearing-fault maintenance plans
  (no RUL; preliminary evidence). We found no close equivalent of our full combination (RUL model + explanation + RAG +
  agent + human approval), though the search was limited.
**Decision (D-002, Option A).** FD001 is the primary dataset for the whole platform. After FD001 is done in Phase 1, run
the same pipeline once on FD002 as a benchmark. FD003/FD004 are out of scope.
**What to learn from it.**
- *Why per-condition normalisation (FD002):* a sensor reading depends on the flight condition as well as engine health,
  so the same raw value means different things in different conditions; we normalise within each condition first.
- *Why we compare against our own baselines:* results depend on protocol (cap, window, scoring), so the honest comparison
  is our models vs our baselines under one fixed protocol, using paper numbers only as a sanity range.
- Keep the scope small enough to finish and explain: simple systems that work beat complex ones that only look impressive.
**Sources:** Saxena et al. 2008 (NASA PHM08); Chaoub et al. 2021 (arXiv 2104.05049); Akbari Pour et al. 2025
(arXiv 2511.04723); Dimidov & Frank 2026 (PHME vol. 9); PARAM 2025 (arXiv 2508.04714).

## Entry 8 - Housekeeping: working agreement and scope made official (2026-10-08)
**What we did.** Added the working agreement (ask first, diary, Colab loop, notebook-first style) to `CLAUDE.md`, and
updated three stale lines that still said "FD002-FD004" (ROADMAP, CLAUDE.md, `configs/data.yaml`) to match decision D-002.
**Why.** `CLAUDE.md` is what any future Claude session reads first, so the rules you set must live there, and the docs must
not contradict each other.
**What to learn from it.** Keep one source of truth: when a decision changes, update every file that states it, or the
project quietly contradicts itself.

## Entry 9 - Master working instructions saved (2026-10-08)
**What we did.** Saved your 31-section MASTER PROJECT INSTRUCTIONS verbatim as `docs/WORKING_INSTRUCTIONS.md` (with a short
note at the top about the one conflict below) and added a condensed summary to `CLAUDE.md`.
**Why.** Future sessions read `CLAUDE.md` first. A short summary there keeps the rules always loaded, and the full file
keeps the exact wording for reference. Rules that live only in a chat get lost.
**Decision.** The instructions conflict with your earlier rule: sections 25-26 say "make an assumption and proceed", but
you told me "don't do anything without asking". You chose: **ask before acting; assume freely only in explanations**.
So I propose each action and wait for your OK before creating, changing, deleting or running anything.
**What else the instructions change.** Experiments get a written hypothesis, baseline, metrics and success criteria
before they run; results get analysed before any model change; comparison tables record cost and parameter counts;
error analysis (worst engines, per-stage) becomes part of each model step; new concepts get a short teach-first note.
**What to learn from it.** When two instructions conflict, resolve it explicitly and write the resolution down in the
place the rules live, so nobody (including a future Claude session) has to guess.

## Entry 10 - Decision D-006: Colab notebook-first workflow (2026-10-08)
**What we did.** Added D-006 to `docs/DECISIONS.md`, recording how we work: write core ML code in Colab notebooks first,
then promote it to tested `src/rulforge/` modules; the first Colab cell clones the GitHub repo.
**Why.** You asked for this workflow earlier, but it only lived in the chat and `CLAUDE.md`. A decision log entry also
records the alternatives we rejected, which is what you will want when explaining the project in an interview.
**What to learn from it.** A decision record has context, decision, alternatives, why, trade-off and a revisit condition.
The trade-off here is real: we write code twice, so promotion must not be skipped.

## Next
Step 2 - EDA notebook on Colab: reproduce the old findings on corrected data, test the RUL cap, fix stage thresholds with a
written justification before any model sees them. (Waiting for your OK to start.)
