# RULForge — Claude Code Project Brief & Implementation Plan

## 1. Project Identity

**Project:** RULForge  
**Type:** End-to-end AI/ML predictive maintenance platform  
**Primary domain:** Industrial predictive maintenance  
**Dataset:** NASA C-MAPSS Turbofan Engine Dataset  
**Primary goal:** Predict Remaining Useful Life (RUL) of industrial machinery from sensor/time-series data, understand why the model made its prediction, and eventually combine the ML system with engineering knowledge, RAG, and agentic workflows.

RULForge is not intended to be a generic chatbot. The core intelligence must come from properly trained and evaluated time-series ML models. GenAI is an additional layer used for knowledge retrieval, explanation, orchestration, and maintenance assistance.

---

## 2. The Real-World Problem

Industrial machines generate continuous sensor data. As equipment degrades, sensor patterns change.

The system should help answer:

- How much useful life does this machine have left?
- Is the machine entering a degradation stage?
- Which sensors/features influenced the prediction?
- What engineering knowledge is relevant to this condition?
- What maintenance action might be appropriate?
- How confident/reliable is the system?
- When should a human engineer review the recommendation?

The final system should behave like a decision-support platform for maintenance engineers, not an autonomous system that makes consequential maintenance decisions without human review.

---

## 3. Final Vision

The long-term RULForge pipeline is:

Sensor Data
→ preprocessing
→ feature engineering
→ ML model
→ RUL prediction
→ degradation-stage prediction
→ explainability
→ engineering knowledge retrieval (RAG)
→ LLM synthesis
→ agentic investigation/workflow
→ maintenance recommendation
→ human engineer approval

Production layer:

FastAPI + Docker + tests + MLflow + CI/CD + monitoring + cloud deployment.

---

## 4. Important Architectural Separation

Keep these responsibilities separate:

### ML models
Responsible for:
- RUL prediction
- degradation-stage classification

Possible models:
- XGBoost
- LSTM
- Attention LSTM
- future temporal Transformer/ensemble if justified

### Explainability
Responsible for:
- SHAP for tree models
- attention visualization for attention-based models
- feature importance
- model diagnostics

Important: attention weights are an interpretability signal, NOT proof of causality.

### RAG
Responsible for:
- retrieving relevant engineering/maintenance documents
- providing evidence for recommendations
- grounding LLM responses in source material

### LLM
Responsible for:
- synthesizing model outputs and retrieved evidence
- explaining results in understandable language
- generating structured maintenance-support text

The LLM must NOT replace the numerical RUL model.

### Agent
Responsible for:
- orchestrating tools
- investigating a machine
- deciding which tool to call next
- combining prediction, sensor history, explanations and retrieved knowledge
- producing a structured recommendation

### Human
Responsible for:
- final consequential maintenance decisions

---

# 5. Current Status

The previous version of RULForge contained experiments involving:

- NASA C-MAPSS
- RUL calculation and cleaning
- RUL clipping around 125 cycles
- rolling sensor features
- XGBoost
- LSTM
- Attention LSTM
- degradation-stage classification
- SHAP experiments
- attention visualization

Some notebooks, checkpoints, and experiment files are now missing or inconsistent.

Therefore:

## We are rebuilding the project cleanly.

Do NOT assume old metrics or model files are still available.

Historical results may be used only as context. All important results must be reproduced in the new pipeline.

---

# 6. Immediate Goal

The first goal is NOT RAG, agents, AWS, or a fancy frontend.

First make the ML foundation correct and reproducible.

Priority:

1. Repository setup
2. Dataset ingestion
3. Exploratory data analysis
4. Correct RUL generation
5. Preprocessing
6. Feature engineering
7. Baseline models
8. XGBoost
9. LSTM
10. Attention LSTM
11. Degradation-stage classification
12. Proper evaluation
13. SHAP
14. Attention visualization
15. Experiment tracking
16. Reproducibility

Only after this is stable should production and GenAI layers begin.

---

# 7. Proposed Repository

```text
RULForge/
│
├── README.md
├── CLAUDE.md
├── PROJECT_PLAN.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── DECISIONS.md
├── EXPERIMENTS.md
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_baselines.ipynb
│   ├── 05_xgboost.ipynb
│   ├── 06_lstm.ipynb
│   ├── 07_attention_lstm.ipynb
│   ├── 08_stage_classification.ipynb
│   ├── 09_explainability.ipynb
│   └── 10_model_comparison.ipynb
│
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── training/
│   ├── evaluation/
│   └── explainability/
│
├── configs/
├── models/
├── tests/
│
├── api/
├── rag/
├── agents/
├── frontend/
├── docker/
├── infrastructure/
│
└── .github/
    └── workflows/
```

Notebooks are for experimentation and visualization.

Reusable production logic should eventually live inside `src/`.

---

# 8. Phase 1 — Data & ML Foundation

## Step 1: Dataset

Use NASA C-MAPSS, initially starting with FD001.

Document:

- dataset structure
- engine IDs
- cycles
- operational settings
- sensor columns
- train/test structure
- ground-truth RUL availability
- degradation behavior

Do not blindly copy preprocessing code from old notebooks.

---

## Step 2: RUL Generation

Implement and document the RUL calculation.

Verify:

- RUL decreases correctly with cycle
- RUL is calculated independently per engine
- engine boundaries are respected
- no future information leaks into training features
- clipping strategy is explicit and configurable

Example:

```text
RUL = max_cycle(engine) - current_cycle
```

If clipping is used:

```text
RUL = min(RUL, RUL_CAP)
```

The cap must be configurable rather than hardcoded throughout the codebase.

---

## Step 3: Preprocessing

Handle:

- column naming
- missing values
- constant sensors
- scaling
- normalization
- operational settings
- irrelevant features

Every preprocessing decision must be documented.

Avoid data leakage.

Fit transformations only on training data where appropriate.

---

# 9. Phase 2 — Feature Engineering

Start simple.

Potential features:

- raw sensors
- cycle
- normalized sensor values
- rolling mean
- rolling standard deviation
- rate of change
- sensor deltas

Rolling features should respect engine boundaries.

Example:

```text
sensor_t
rolling_mean_5
rolling_std_5
delta_1
```

Do not create dozens of engineered features without validating whether they improve performance.

---

# 10. Phase 3 — Baselines

Before deep learning, establish simple baselines.

Possible sequence:

1. naive baseline
2. Linear Regression
3. Random Forest
4. XGBoost

Track:

- RMSE
- MAE
- R²
- training time
- inference time

The purpose is to establish a meaningful benchmark.

---

# 11. Phase 4 — Deep Learning

Implement:

## LSTM

Use sequences of sensor observations.

Document:

- sequence length
- hidden dimension
- number of layers
- dropout
- optimizer
- learning rate
- batch size
- epochs
- loss function

## Attention LSTM

Add an attention mechanism over the sequence.

Outputs:

```text
RUL regression
+
degradation-stage classification
```

This creates a multi-task learning setup.

Do not assume the architecture is optimal. Compare experiments.

---

# 12. Degradation Stage

Create a clearly defined degradation-stage formulation.

Possible example:

```text
Stage 0 → healthy
Stage 1 → early degradation
Stage 2 → severe degradation
```

But the exact thresholds/classes must be justified and documented.

Evaluate:

- accuracy
- precision
- recall
- F1
- confusion matrix

Do not change class definitions just to improve the score.

---

# 13. Evaluation

Every model must be evaluated using the same data split and methodology.

Primary RUL metrics:

- RMSE
- MAE
- R²

Classification metrics:

- Accuracy
- Precision
- Recall
- F1
- Confusion Matrix

Engineering metrics:

- inference latency
- model size
- training time

Avoid cherry-picking the best experiment.

Record all meaningful experiments.

---

# 14. Explainability

## XGBoost

Use SHAP.

Generate:

- global feature importance
- summary plot
- individual prediction explanation

## Attention LSTM

Visualize attention across sequence timesteps.

Important:

Attention visualization should be presented as an interpretability aid, not causal proof.

---

# 15. Experiment Tracking

Use MLflow once the first reliable experiments exist.

Track:

- model type
- parameters
- dataset version
- feature configuration
- metrics
- training time
- artifacts
- model version

Example:

```text
Experiment
    ├── parameters
    ├── metrics
    ├── model
    ├── plots
    └── configuration
```

---

# 16. Phase 5 — ML Engineering

Once the model is stable:

Refactor reusable logic into `src/`.

Create:

- configuration management
- model loading
- inference pipeline
- preprocessing pipeline
- evaluation utilities
- logging

Build a FastAPI service.

Initial endpoints:

```text
GET  /health
GET  /model/info
POST /predict
POST /predict/batch
POST /explain
```

Do not build unnecessary endpoints.

---

# 17. Phase 6 — Testing

Create tests for:

```text
tests/
├── test_preprocessing.py
├── test_features.py
├── test_models.py
├── test_evaluation.py
├── test_api.py
├── test_rag.py
├── test_agent.py
└── test_integration.py
```

Important edge cases:

- missing sensor values
- invalid input
- insufficient sequence length
- engine boundary problems
- model loading failure
- prediction failure
- retrieval failure
- LLM failure
- invalid tool calls
- API errors

---

# 18. Phase 7 — MLOps

Add:

- MLflow
- Docker
- GitHub Actions
- reproducible training
- model versioning
- structured logging
- basic monitoring

DVC can be considered if dataset/model artifact versioning becomes necessary.

Do not add infrastructure simply for resume keywords.

---

# 19. Phase 8 — RAG

Only begin after the ML system works.

Create a small, curated engineering knowledge base.

Possible documents:

- maintenance manuals
- equipment documentation
- sensor descriptions
- fault descriptions
- maintenance procedures
- engineering references

Pipeline:

```text
Documents
→ parsing
→ cleaning
→ chunking
→ embeddings
→ vector database
→ retrieval
→ optional reranking
→ LLM
```

The system should cite retrieved sources.

Evaluate retrieval quality instead of assuming RAG works.

---

# 20. Phase 9 — Agentic AI

Build a Maintenance Agent using tools.

Potential tools:

```text
get_engine_data()
predict_rul()
get_sensor_history()
explain_prediction()
retrieve_maintenance_docs()
get_engine_history()
calculate_risk()
generate_report()
```

Possible workflow:

```text
User Question
      ↓
Analyze Request
      ↓
Get Engine State
      ↓
Predict RUL
      ↓
Analyze Risk
      ↓
Explain Prediction
      ↓
Retrieve Engineering Knowledge
      ↓
Generate Recommendation
      ↓
Validate
      ↓
Human Approval
```

Use LangGraph if it provides useful stateful orchestration.

Do not make the agent autonomous merely for the sake of using agents.

---

# 21. Optional MCP Layer

MCP can later expose RULForge capabilities as standardized tools.

Possible MCP tools:

```text
get_engine_data
predict_rul
explain_prediction
retrieve_maintenance_docs
get_engine_history
```

MCP is optional and should be added only after the underlying tools are stable.

---

# 22. Phase 10 — Frontend

Build a professional dashboard.

Potential screens:

### Dashboard

- engine health
- predicted RUL
- degradation stage
- risk level
- recent sensor trends

### Explainability

- SHAP
- feature importance
- attention visualization

### Maintenance Assistant

- natural-language questions
- evidence-backed answers
- retrieved sources
- recommendation
- confidence/limitations

Avoid making the frontend more complex than the backend capabilities justify.

---

# 23. Phase 11 — Cloud

Potential AWS architecture:

```text
Frontend
   ↓
API
   ↓
Containerized Services
   ↓
ML Model
   ↓
Database / Object Storage
```

Potential services may include:

- S3
- ECS/Fargate
- RDS/PostgreSQL
- CloudWatch
- IAM
- Secrets Manager

SageMaker is optional.

Choose services based on actual requirements and cost, not keywords.

---

# 24. Security

Never commit:

- API keys
- passwords
- cloud credentials
- `.env` secrets

Use:

- environment variables
- secret management
- input validation
- authentication
- authorization
- least-privilege IAM
- dependency scanning
- container scanning
- secure logging

High-risk maintenance recommendations should require human approval.

---

# 25. Evaluation Beyond ML

Eventually evaluate three layers.

## ML

- RMSE
- MAE
- R²
- classification metrics
- latency

## RAG

- retrieval relevance
- context precision
- context recall
- citation correctness
- faithfulness

## Agent

- tool selection accuracy
- task completion
- invalid tool calls
- hallucination rate
- latency
- cost

---

# 26. Development Rules for Claude Code

Claude Code should behave like an engineering partner, not blindly rewrite the project.

### Rule 1 — Inspect before modifying

Before writing code:

- inspect the repository
- inspect existing files
- understand dependencies
- identify current state
- explain what needs to change

### Rule 2 — Do not rewrite unnecessarily

Prefer small, coherent changes.

### Rule 3 — Explain architecture

For significant changes, explain:

- why it is needed
- what it does
- what files change
- what assumptions exist
- how it will be tested

### Rule 4 — Test changes

After implementation:

- run tests
- run relevant scripts
- validate outputs
- report failures honestly

### Rule 5 — No fake results

Never invent:

- metrics
- benchmark results
- successful deployment
- test results
- model performance

### Rule 6 — Reproducibility

Every experiment should have:

- configuration
- random seed where appropriate
- dataset information
- metrics
- model configuration
- experiment record

### Rule 7 — Dependencies

Do not add a dependency unless it is actually needed.

Explain why it is being added.

### Rule 8 — ML correctness

Pay special attention to:

- leakage
- train/test contamination
- sequence construction
- engine boundaries
- scaling
- label generation
- evaluation methodology

### Rule 9 — AI-assisted coding

AI can write implementation code.

But the resulting code must remain understandable and maintainable by the project owner.

For important components, provide a concise explanation of the logic.

---

# 27. Anti-Vibecoding Checklist

Before accepting important generated code, the developer should be able to answer:

1. What does this code do?
2. Why is it needed?
3. What are its inputs?
4. What are its outputs?
5. What assumptions does it make?
6. What can fail?
7. How is it tested?
8. How does it fit into RULForge?

For ML code additionally:

1. What is the target?
2. What is the loss?
3. Why this model?
4. How is the sequence created?
5. Could there be leakage?
6. Why this metric?
7. What does the result mean?
8. Where does the model fail?

---

# 28. Definition of Done

RULForge is successful when a user can provide machine sensor data and the system can:

1. validate the data
2. preprocess it
3. generate features
4. predict RUL
5. classify degradation stage
6. explain the prediction
7. retrieve relevant engineering evidence
8. synthesize an evidence-grounded explanation
9. use tools through an agentic workflow
10. generate a maintenance-support recommendation
11. expose the system through an API
12. run through Docker
13. have tests
14. track experiments/models
15. be deployable to cloud infrastructure
16. maintain human approval for consequential decisions

---

# 29. What NOT To Do Yet

Do NOT start with:

- RAG
- LangGraph
- MCP
- AWS
- complex frontend
- multi-agent systems
- autonomous maintenance actions

until the ML foundation is reproducible.

The correct order is:

```text
DATA
 ↓
ML
 ↓
EVALUATION
 ↓
EXPLAINABILITY
 ↓
ML ENGINEERING
 ↓
MLOps
 ↓
RAG
 ↓
AGENTS
 ↓
CLOUD
 ↓
PRODUCTION HARDENING
```

---

# 30. First Claude Code Task

When this project is first opened in Claude Code, DO NOT immediately write the whole application.

First:

1. Read this document.
2. Inspect the repository.
3. Check what files currently exist.
4. Identify whether the repository is empty, partial, or contains old RULForge work.
5. Do not delete anything.
6. Produce a repository audit.
7. Propose the Phase 1 implementation plan.
8. Identify missing information or risky assumptions.
9. Wait for approval before making major implementation changes.

The first implementation target should be:

**A clean, reproducible NASA C-MAPSS data pipeline with verified RUL generation and preprocessing.**

After that, proceed milestone by milestone.

---

# 31. Core Philosophy

RULForge should demonstrate that the developer understands:

**Machine Learning + Deep Learning + Time-Series Data + Explainability + ML Engineering + MLOps + RAG + LLMs + Agentic AI + Cloud**

But complexity must be earned.

Every new technology must solve a real problem in the system.

The goal is not to say:

> "I used AI everywhere."

The goal is to demonstrate:

> "I understand the complete lifecycle of building, evaluating, deploying, and operating an AI system."

