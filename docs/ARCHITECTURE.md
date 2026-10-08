# Architecture

Target (built phase by phase; see ROADMAP):

```
User -> Dashboard -> FastAPI -> Prediction service (XGBoost / (Attention-)LSTM)
                              -> Explainability (SHAP / attention / IG)
                              -> Agent (LangGraph) -> tools: predict, history, explain, RAG, risk
                                                   -> RAG -> vector DB -> LLM -> cited answer
                                                   -> human approval
Infra: GitHub Actions -> Docker -> AWS | MLflow | PostgreSQL | vector DB | logging
```

Responsibilities: ML predicts; explainability explains the model; RAG retrieves evidence; the LLM
communicates; agents orchestrate; humans decide. Prediction is separate from explanation, retrieval
from generation, and tools from agent reasoning.

Code layout: one installable package `src/rulforge/` shared by training, API, and agent tools.
`inference/` is the single predict path (same preprocessing + scaler as training).
