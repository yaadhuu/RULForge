# Roadmap

Legend: [ ] not started · [~] in progress · [x] done. Update when state changes.

## Phase 1 - ML foundation (current)
- [~] Repo setup, environment, `download_data.py` (verified in cloud; confirm on your machine)
- [ ] EDA (FD001): structure, constant sensors, degradation curves; fix stage thresholds with justification
- [x] RUL generation + cap, with alignment test (engines 1/2/3 -> 112/98/69)  [Step 1; 13 tests pass, mutation-checked]
- [ ] Preprocessing + engine-level train/validation split + leakage tests
- [ ] Features (raw, rolling, lag/delta) validated by ablation, not assumed
- [ ] Baselines: naive, Linear Regression, Random Forest, XGBoost
- [ ] LSTM, Attention-LSTM (RUL only vs multi-task), optional 1D-CNN/TCN
- [ ] Standard metrics incl. NASA score, last-cycle test protocol, multi-seed reporting
- [ ] Seed-ensemble uncertainty
- [ ] SHAP (XGBoost) + attention / Integrated Gradients (sequence model)
- [ ] Extend the pipeline to FD002 as one extra benchmark after FD001 is done (FD003/FD004 out of scope, D-002)

## Phase 2 - ML engineering: `inference/`, config management, FastAPI (/health, /predict, /predict/batch, /model/info, /explain), tests
## Phase 3 - MLOps: MLflow, Docker, GitHub Actions, logging, basic monitoring
## Phase 4 - RAG: curated knowledge base, embeddings, vector DB, citations, retrieval/faithfulness evaluation
## Phase 5 - Agent: tools (plain tested functions) -> LangGraph workflow -> human approval -> agent evaluation
## Phase 6 - AWS deployment (cost-conscious)
## Phase 7 - Production hardening: auth, validation, rate limits, scanning, observability
## Phase 8 - Showcase: README benchmarks, demo video, experiment/evaluation reports
