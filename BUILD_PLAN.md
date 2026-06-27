# ClimateChain — Portfolio Build Plan

> **Goal of this document:** Turn ClimateChain from a coursework data-mining script into a
> *credible, end-to-end, portfolio-grade* project that a hiring manager (data engineer / ML
> engineer / data scientist) looks at and thinks: *"This person can ship."*
>
> This plan is written from three lenses, deliberately blended in every phase:
> - **Systems Architect** — boundaries, data flow, reproducibility, scalability.
> - **Software Engineer** — tests, CI, config, secrets, packaging, code quality.
> - **End User** — can a non-author actually run it, trust it, and learn something?

---

## 0. The honest positioning (read this first)

The single biggest weakness today is **credibility of the claims**, not the code quality. The
project currently asserts it predicts disaster cascades, but association-rule "confidence" is just
historical co-occurrence frequency — it is **never validated against held-out future data**. A
sharp interviewer will catch this in 30 seconds.

So the **north star of this rebuild is one sentence:**

> *"I can prove, with backtesting, whether my model predicts cascading disasters better than a naive baseline — and I'm honest about where it doesn't."*

That single shift (from "look at these rules" → "here is measured predictive skill vs. a baseline")
is what converts this from a school project into a portfolio centerpiece.

### Strategic decisions (the "evolve in the right direction" part)

| Decision | Choice | Why |
|---|---|---|
| **Keep association rules?** | **Yes — as an *explainable baseline*, not the headline.** | Don't throw away working code. Reframe it as the interpretable layer. |
| **Add a real predictive model?** | **Yes** — a proper supervised temporal model with backtesting. | This is the credibility upgrade. |
| **Go broad or deep?** | **Deep.** Lock scope to a well-covered region + 2–3 concrete cascades. | A narrow thing that *demonstrably works* beats a broad thing that's only suggestive. |
| **Real-time?** | **No.** Stay batch/historical, but make it reproducible. | Real-time is a cost/complexity trap with no portfolio payoff. |
| **Blockchain?** | **No.** Rename perception cleanly: "chain" = disaster cascade chain. | Avoid the false implication. Own the naming in the README. |
| **Deployment** | One-command local (Docker Compose) + one hosted demo (Streamlit Cloud). | "Click here to try it" is worth 10 paragraphs of README. |

---

## 1. Target architecture

```
                          ┌─────────────────────────────────────────────┐
                          │                 SOURCES                      │
                          │   NOAA Storm Events CSV   NASA POWER API     │
                          └───────────────┬─────────────────┬───────────┘
                                          │                 │
                                          ▼                 ▼
                       ┌──────────────────────────────────────────────┐
                       │   INGESTION LAYER  (src/ingestion/)           │
                       │   - download + cache raw to data/raw/         │
                       │   - schema validation (pandera/pydantic)      │
                       │   - data versioning manifest (hash + date)    │
                       └───────────────────────┬──────────────────────┘
                                               ▼
                       ┌──────────────────────────────────────────────┐
                       │   TRANSFORM LAYER  (src/transform/)           │
                       │   - clean, discretize, state-month baskets    │
                       │   - NASA/NOAA fusion + temporal lag features  │
                       │   - anomaly (IsolationForest) + clusters      │
                       │   - OUTPUT: tidy feature table (parquet)      │
                       └───────────────────────┬──────────────────────┘
                                               ▼
                ┌──────────────────────────────┴───────────────────────────┐
                ▼                              ▼                             ▼
   ┌────────────────────┐      ┌──────────────────────────┐   ┌────────────────────────┐
   │  BASELINE MODEL    │      │   PREDICTIVE MODEL        │   │   STORE (MongoDB/parquet)│
   │  Association rules  │      │   Gradient-boosted /      │   │   features + predictions │
   │  (explainable)      │      │   logistic temporal model │   │   + run metadata         │
   └─────────┬──────────┘      └────────────┬─────────────┘   └────────────┬───────────┘
             │                              │                              │
             │           ┌──────────────────┴───────────────┐             │
             │           │   EVALUATION (src/evaluation/)    │             │
             │           │   walk-forward backtest, metrics, │             │
             │           │   calibration, vs-baseline report │             │
             │           └──────────────────┬───────────────┘             │
             └──────────────────────────────┴──────────────────────────────┘
                                            ▼
                       ┌──────────────────────────────────────────────┐
                       │   PRESENTATION  (app/)                        │
                       │   Streamlit: Rules • Predictions • Backtest   │
                       │   • Map • Methodology/Honesty page            │
                       └──────────────────────────────────────────────┘
```

**Key architectural changes vs. today:**
1. Numbered `phaseN_*.py` scripts → a clean **`src/` package + a single orchestrator** (CLI or `Makefile`).
2. JSON intermediates → **parquet** feature tables (typed, fast, smaller).
3. Add an **evaluation layer** (this is the new heart of the project).
4. MongoDB stays, but becomes **optional** (parquet is the source of truth; Mongo is a queryable serving copy) so the repo runs with zero external services.

---

## 2. End-user perspective (personas & their "definition of useful")

| Persona | What they do | What must be true for them |
|---|---|---|
| **Recruiter / hiring manager** | Skims README + clicks live demo for 90 seconds | Clear story, screenshots, "Try it" link, honest results section |
| **Engineer reviewing code** | Clones, runs `make demo`, reads `src/` | One command works on sample data; tests pass; clean structure |
| **Domain-curious user** | Plays with the dashboard | Can pick a state/cascade, see a prediction + how confident, understand the map |
| **Future you (6 months later)** | Extends the project | Docs explain *why*, not just *what*; reproducible from scratch |

**User-experience requirements that flow from this:**
- It must run with **bundled sample data** so nobody is blocked on a 2 GB NOAA download.
- The dashboard must have a **"Methodology & Honesty" page** that states limitations plainly (this *builds* trust, it doesn't reduce it).
- Every number on screen must be traceable to a metric you can defend.

---

## 3. Phased roadmap

Each phase is independently shippable. Stop after any phase and you still have something better than today. Effort is rough solo-dev calendar estimate.

---

### Phase 1 — Foundation & hygiene  *(must-do, ~2–4 days)*

**Architect:** make the repo reproducible and safe.
**Engineer:** establish the quality bar everything else builds on.

- [ ] **Rotate the leaked MongoDB credentials** currently in `.env`, and confirm `.env` is gitignored. Add `.env.example` with placeholder keys. *(Security — do this first.)*
- [ ] Add a real **`README.md`**: one-paragraph pitch, architecture diagram, screenshots, quickstart, honest "limitations" section, and the "chain = cascade, not blockchain" clarification.
- [ ] Restructure into a proper package:
  ```
  src/climatechain/
    ingestion/  transform/  models/  evaluation/  storage/  config.py
  app/            # streamlit
  scripts/        # thin CLI entrypoints / orchestrator
  tests/
  data/sample/    # COMMITTED tiny dataset
  ```
- [ ] Replace the numbered `phaseN_*.py` scripts with a single **orchestrator** (`python -m climatechain.run all` or a `Makefile`: `make ingest transform train evaluate app`). Fix the current run-order trap (Phase 2 depends on Phase 6 output).
- [ ] Pin dependencies properly (`requirements.txt` + optionally `pyproject.toml`). Add `ruff` (lint+format) and `pre-commit`.
- [ ] **Commit a small sample dataset** (one region, a few years) so the project runs offline with zero setup.

**Acceptance criteria:** A stranger runs `make demo` (or 2 documented commands) on a fresh clone with no MongoDB, no secrets, no big download — and sees the dashboard with real (sample) results.

---

### Phase 2 — Data integrity & honest features  *(must-do, ~3–5 days)*

**Architect:** trustworthy inputs; no silent corruption.
**Engineer:** validated, typed, tested transforms.

- [ ] Add **schema validation** at ingestion (`pandera` or `pydantic`): column types, value ranges, expected categories. Fail loudly, not silently.
- [ ] Fix known data-quality shortcuts: `fillna(0)` for missing damage/magnitude hides missingness — replace with explicit `MISSING` handling or documented imputation, and **add a missingness indicator** rather than pretending zeros are real.
- [ ] Expand **NASA coverage** from the hardcoded 10 states to the full target region (or explicitly document and justify the chosen region). Add humidity/wind only if you actually use them — otherwise delete the claim from the docs.
- [ ] Convert intermediates to **parquet** with a small **data manifest** (source hash, row counts, date generated) for reproducibility.
- [ ] **Resolve doc/code drift:** either implement or remove every aspirational claim (OLAP, redundant-rule pruning, county granularity, event-level schemas). *Docs that match code > docs that oversell.*

**Acceptance criteria:** `pytest tests/test_transform.py` passes; running ingestion twice is deterministic; the report/README describe only what the code actually does.

---

### Phase 3 — The credibility upgrade: prediction + backtesting  *(the headline phase, ~5–8 days)*

This is what makes the project portfolio-worthy. **Do not skip.**

**Architect:** separate "fit" from "predict" from "evaluate"; no leakage across time.
**Data scientist:** measure real predictive skill honestly.

- [ ] **Reframe the problem as supervised prediction:** for each (state, month), using only features known *up to* time *t* (the existing T-1/T-2/T-3 lag features are perfect for this), predict whether disaster *D* occurs in month *t* (or *t+1*).
- [ ] Pick **2–3 concrete cascade targets** (e.g., drought→wildfire, heat→flash-flood) instead of "all disasters." Narrow and provable.
- [ ] Build a **baseline stack** so improvements are measurable:
  1. *Naive base rate* (always predict the historical monthly frequency).
  2. *Seasonal baseline* (per-month-of-year frequency).
  3. *Association-rule model* (your existing engine, reframed as a classifier).
  4. *Supervised model* (logistic regression → gradient boosting / `xgboost`/`lightgbm`).
- [ ] Implement **walk-forward (time-series) cross-validation** — train on past, test on future. **Never** random-split time-series data. This is the #1 thing that signals you know what you're doing.
- [ ] Report proper metrics for rare events: **PR-AUC, Brier score, calibration curve, lift@k**, and lead-time. Accuracy alone is meaningless for rare disasters.
- [ ] Produce a **`MODEL_CARD.md`**: data, target definition, metrics vs. each baseline, calibration, failure modes, and explicit limitations.

**Acceptance criteria:** A reproducible backtest report shows your model's skill vs. baselines on held-out future months, with calibration and the honest verdict (even if the verdict is "marginally better than seasonal baseline" — that's a *credible* result).

---

### Phase 4 — Serving & storage  *(should-do, ~2–3 days)*

**Architect:** clean separation of compute vs. serving.

- [ ] Make **parquet the source of truth**; MongoDB becomes an optional serving/query layer loaded from parquet. App falls back to parquet if Mongo isn't configured (so the demo always works).
- [ ] Persist **model artifacts + predictions + run metadata** (timestamp, data hash, metrics) so the dashboard shows "as of" provenance.
- [ ] Add lightweight **experiment tracking** (even a CSV/JSON run log, or MLflow if you want to show the tool) so results are reproducible and comparable.

**Acceptance criteria:** App runs with `STORAGE=parquet` (no Mongo) *and* with `STORAGE=mongo`, controlled by one env var.

---

### Phase 5 — Dashboard & UX overhaul  *(should-do, ~3–4 days)*

**End user:** make it understandable and trustworthy at a glance.

- [ ] Restructure tabs into a clear narrative:
  1. **Overview** — what this is, the headline result, a US/region **choropleth map** of risk.
  2. **Predictions** — pick state + cascade → predicted probability, **calibration-aware** language ("when we say 70%, it happens ~68% of the time"), and lead time.
  3. **Explainability** — the association-rule network + feature importances behind a prediction.
  4. **Backtest** — the honest evaluation: model vs. baselines, calibration plot, PR curves.
  5. **Methodology & Honesty** — assumptions, limitations, what this is *not*.
- [ ] Fix the current overstatement in the UI (e.g., the hardcoded "40% → 80%" insight box) — replace with **dynamically computed, defensible** numbers from the backtest.
- [ ] Add a **map view** (state-level choropleth via `plotly`/`pydeck`) — far more intuitive than only a node graph.
- [ ] Polish: loading states, empty states, tooltips explaining support/confidence/lift/calibration.

**Acceptance criteria:** A non-technical user can pick a region, get a prediction, and correctly explain "how confident should I be and why."

---

### Phase 6 — Testing, CI/CD, deployment  *(should-do, ~2–3 days)*

**Engineer:** prove it works and keep it working.

- [ ] **Unit tests** for transforms (lagging, discretization, fusion) and **a regression test** that asserts backtest metrics stay within a tolerance band.
- [ ] **GitHub Actions**: lint (`ruff`) → tests (`pytest`) → build. A green badge in the README is cheap credibility.
- [ ] **Dockerfile + docker-compose** (app + optional Mongo) for one-command local run.
- [ ] **Deploy a live demo** (Streamlit Community Cloud / Hugging Face Spaces / Render) backed by the committed sample data. Put the link at the top of the README.

**Acceptance criteria:** Green CI badge; `docker compose up` serves the app; a public URL works.

---

### Phase 7 — Stretch goals  *(nice-to-have, optional)*

Only after 1–6. Pick based on the role you're targeting.

- [ ] **County-level granularity** for one state (finally delivers the long-promised resolution → much more actionable).
- [ ] **SHAP** explanations for individual predictions (great DS portfolio signal).
- [ ] **FastAPI** prediction endpoint (signals backend/ML-engineering skills).
- [ ] **Airflow/Prefect/Dagster** DAG for the pipeline (signals data-engineering skills).
- [ ] Simple **drift monitoring** on incoming data.

---

## 4. Concrete fixes mapped to current code

| Current file | Issue | Action | Phase |
|---|---|---|---|
| `.env` | Live Atlas credentials committed | Rotate, gitignore, add `.env.example` | 1 |
| `phase2..phase10_*.py` | Numbered scripts, fragile run order | Merge into `src/climatechain/` + orchestrator | 1 |
| `src/data_pipeline/cleaner.py` | `fillna(0)` hides missing magnitude | Explicit missing handling + indicator | 2 |
| `src/data_pipeline/nasa_power.py` | Hardcoded 10 states | Expand region or document scope | 2 |
| `phase6_integration.py` | JSON intermediates, brittle ID string ops | Parquet + typed keys + tests | 2 |
| `src/mining/association_rules.py` | "Confidence" presented as prediction | Reframe as baseline classifier + backtest | 3 |
| `dashboard_app.py` (L182) | Hardcoded "40%→80%" claim | Replace with computed backtest numbers | 5 |
| `dashboard_app.py` | Re-queries Mongo in multiple funcs | Single data layer, parquet fallback | 4 |
| `src/config.py` | County option exists but unused | Implement (stretch) or remove claim | 2/7 |
| Docs (report/overview) | Claim OLAP, pruning, humidity/wind | Implement or delete claims | 2 |
| Whole repo | No tests/CI/Docker/README | Add all four | 1/6 |

---

## 5. Definition of Done (portfolio checklist)

The project is "portfolio complete" when **all** of these are true:

- [ ] A stranger can go from `git clone` → working dashboard in **one command** on sample data.
- [ ] There's a **live demo URL** at the top of the README.
- [ ] The README has the pitch, architecture diagram, screenshots, and an honest **Limitations** section.
- [ ] A **backtest** proves (or honestly disproves) predictive skill **vs. explicit baselines**, using **time-aware** validation.
- [ ] A **MODEL_CARD.md** documents target, metrics, calibration, and failure modes.
- [ ] **Tests pass in CI** (green badge).
- [ ] **No secrets** in the repo; docs match code (no overselling).
- [ ] Every number on the dashboard is **traceable and defensible**.

---

## 6. Suggested order & "if you only have a weekend"

**Full path:** Phase 1 → 2 → 3 → 4 → 5 → 6 → (7).

**Minimum high-impact slice (one weekend), if time is tight:**
1. Phase 1 (hygiene, README, sample data, one-command run) — *makes it runnable & safe.*
2. Phase 3 core (one cascade, baselines, walk-forward backtest, metrics) — *makes it credible.*
3. Phase 6 deploy only (live Streamlit link) — *makes it clickable.*

Those three alone move the project further than polishing everything else.

---

## 7. Risks & how to defuse them

| Risk | Likelihood | Mitigation |
|---|---|---|
| Backtest shows model ≈ baseline | **High** | That's still a *great* portfolio result if presented honestly ("here's what worked, what didn't, why"). Honesty is the signal. |
| Scope creep (trying to cover all 48 states + all disasters) | High | Lock scope in Phase 3: one region, 2–3 cascades. Write it down. |
| Data download friction blocks reviewers | High | Commit sample data (Phase 1). Non-negotiable. |
| Time-leakage in validation | Medium | Walk-forward only; assert in tests that train max-date < test min-date. |
| Over-polished UI, weak substance | Medium | Substance (Phase 3) before polish (Phase 5). |

---

### Final note

You've already built the hard plumbing (ingestion, fusion, temporal lagging, Mongo, a working
dashboard). The remaining work is **less about more features and more about credibility and
reproducibility**. Do Phases 1 and 3 well and this stops being "a school project that mines
patterns" and becomes "an engineer who frames a problem, builds a pipeline, validates honestly,
and ships a demo." That's the version that gets you interviews.
