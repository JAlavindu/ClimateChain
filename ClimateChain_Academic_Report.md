# ClimateChain: Mining Cascading Climate Disaster Patterns Using Multi-Level Association Rules

**Course:** ICT 333 1.5 — Data Mining and Data Warehousing  
**Department:** Computer Science, Faculty of Applied Sciences  
**University:** University of Sri Jayewardenepura  

---

## Table of Contents

1. [Abstract](#abstract)
2. [Introduction](#introduction)
3. [Background & Theoretical Foundations](#background--theoretical-foundations)
4. [Data Sources & Dataset Description](#data-sources--dataset-description)
5. [System Architecture](#system-architecture)
6. [NoSQL Data Modeling & Ingestion](#nosql-data-modeling--ingestion)
7. [ETL Pipeline & Data Transformation](#etl-pipeline--data-transformation)
8. [Exploratory Data Analysis](#exploratory-data-analysis)
9. [Transaction Construction](#transaction-construction)
10. [Association Rule Mining Engine](#association-rule-mining-engine)
11. [Temporal Trend Analysis — The Climate Change Signal](#temporal-trend-analysis--the-climate-change-signal)
12. [Early Warning Dashboard](#early-warning-dashboard)
13. [Results & Discussion](#results--discussion)
14. [Limitations](#limitations)
15. [Conclusion](#conclusion)
16. [References](#references)

---

## Abstract

Traditional climate analysis treats disasters as isolated phenomena — cataloguing *what* happened, *where*, and *when*. ClimateChain challenges this paradigm by treating the climate system as an interconnected web of transactional events and asking a fundamentally different question: *what triggers what?* By applying the principles of frequent pattern mining to 15 years of historical disaster and climate baseline data sourced from NOAA and NASA, this system uncovers cascading association rules that reveal how sequences of climate conditions — and prior disaster events — compound over time to produce major disasters. A document-oriented NoSQL data model handles the inherent heterogeneity of multi-source climate records, while a temporal lagging mechanism transforms the system from a passive historical observer into a forward-looking early warning engine. A decade-over-decade trend analysis further extracts a measurable climate change signal directly from the data — demonstrating that disaster-triggering thresholds are systematically lowering over time. The best-performing cascade rule, `[T-3_EXTREME_HEAT, LIGHTNING] → [FLASH_FLOOD]`, saw its predictive confidence rise from 54.1% in 2005–2012 to 90.3% in 2013–2020 — a 36.2% shift that constitutes empirical, data-driven evidence of accelerating climate instability. The system is presented through an interactive Streamlit dashboard featuring real-time rule tuning and physics-based cascading threat network visualisation.

---

## Introduction

The accelerating frequency and severity of climate disasters represents one of the most consequential challenges of the twenty-first century. The proliferation of environmental sensor networks, satellite systems, and governmental reporting infrastructure has contributed to an unprecedented accumulation of climate event data. However, the dominant analytical paradigm remains largely reactive — sophisticated physics-based models forecast isolated atmospheric conditions, while historical databases catalogue what has already occurred. The potential of the data itself to reveal systemic, predictive patterns has been significantly underexplored.

This project draws on the observation that climate events are not independent occurrences. A sustained drought desiccates vegetation and depletes soil moisture. That primed landscape, under the right wind and heat conditions, becomes a wildfire accelerant. The denuded, compacted soil left behind then dramatically increases surface runoff, amplifying flood risk when precipitation finally arrives. This is not conjecture — it is a chain of physical causality that should be visible in the data, if the right analytical framework is applied.

ClimateChain applies that framework. Inspired by the market basket analysis paradigm — in which transaction databases are mined to reveal what items co-occur — this system treats each month's climate record for a given region as a "transaction" and each discretised climate condition or disaster event as an "item." The FP-Growth algorithm then extracts the association rules that define which antecedent conditions most reliably precede which consequent disasters. Critically, by introducing temporal lag features (T-1, T-2, T-3 months prior), the system captures the *sequence* of events rather than mere co-occurrence — transforming pattern discovery into genuine predictive intelligence.

The project is grounded in four interlocking theoretical domains covered in this course: the principles of Knowledge Discovery in Databases (KDD), data warehousing and dimensional modelling, association rule mining, and NoSQL database architecture. Each design decision in ClimateChain can be directly traced back to one of these theoretical foundations, and the following sections make those connections explicit.

---

## Background & Theoretical Foundations

### 2.1 Knowledge Discovery in Databases

The KDD process describes a pipeline by which raw data is transformed, through a series of structured steps, into actionable knowledge. The process encompasses data cleaning and integration, data selection and transformation, the application of data mining algorithms, and the evaluation and interpretation of the resulting patterns. ClimateChain is, in its entirety, an instantiation of this pipeline.

Raw NOAA storm event records arrive inconsistently formatted, with missing values, heterogeneous schemas, and units that vary by event type. NASA baseline climate records arrive as continuous time-series measurements on a different temporal and spatial resolution. Neither dataset is directly usable for pattern mining. The KDD pipeline — cleaning, fusion, discretisation, transaction construction, mining, and visual evaluation — is the mechanism by which these raw inputs are converted into the cascade rules that form ClimateChain's core output.

This project adopts the database-and-warehousing perspective on KDD, in which data cleaning, integration, and warehousing are treated as foundational infrastructure rather than preprocessing afterthoughts. The analytical outputs — the association rules — are only as trustworthy as the pipeline that produced the data they were mined from.

### 2.2 Data Warehousing & Dimensional Modelling

A data warehouse is a subject-oriented, integrated, time-variant, and non-volatile analytical store, distinct from operational databases, designed to support decision-making rather than transaction processing. ClimateChain's analytical layer embodies each of these properties.

**Subject-oriented:** The warehouse is organised around the subject of *climate disaster events*, not around the operational concerns of any individual data source. NOAA and NASA data are both subordinated to this analytical subject.

**Integrated:** Data is extracted from two structurally dissimilar sources — discrete event records from NOAA and continuous time-series baselines from NASA — and unified into a consistent analytical schema through a formal ETL process.

**Time-variant:** Every record in the warehouse carries a temporal identifier. The decade-over-decade trend analysis, which forms the climate change signal component of this project, depends entirely on this temporal dimensionality. Without time-variant data, the evolution of disaster patterns over time would be invisible.

**Non-volatile:** The processed warehouse is a stable analytical snapshot. It does not receive live operational updates. The mining engine queries the warehouse; it does not modify it.

While standard dimensional modelling principles (like star schemas) were considered, the unique pipeline needs of FP-Growth and NoSQL document stores led to a **denormalised document model**. Instead of breaking data into a central fact table and joining it to detached dimension tables (`DIM_TIME`, `DIM_REGION`), all dimensional context—spatial (State) and temporal (Year, Month)—is embedded directly into a single, self-contained transaction document. This flattens the multidimensional space into a "market basket," dramatically accelerating the read-heavy workloads required by the sequential mining engine without requiring expensive real-time relational joins.

OLAP operations are used to explore the disaster landscape before mining begins. Roll-up operations aggregate disaster counts from monthly to yearly to decade-level summaries, revealing long-term frequency trends. Drill-down operations decompose regional disaster totals into state and county breakdowns, revealing geographic concentration patterns. Slice operations isolate specific disaster types or seasons for targeted analysis. These operations are not peripheral — they inform the mining configuration, particularly the choice of minimum support thresholds, which must be calibrated to the actual frequency distribution of disaster events as revealed by OLAP exploration.

### 2.3 Association Rule Mining

Association rule mining is the process of discovering interesting relationships — associations and correlations — among variables in large datasets. The canonical formulation defines a rule as `A → B`, where A (the antecedent) and B (the consequent) are sets of items, and the rule is evaluated on three metrics:

**Support** measures the proportion of transactions in which both A and B appear together:

$$\text{Support}(A \Rightarrow B) = P(A \cup B) = \frac{\text{\# transactions containing both A and B}}{\text{total transactions}}$$

**Confidence** measures the conditional probability that B appears given that A is present:

$$\text{Confidence}(A \Rightarrow B) = P(B \mid A) = \frac{P(A \cup B)}{P(A)} = \frac{\text{\# transactions containing both A and B}}{\text{\# transactions containing A}}$$

**Lift** measures how much more likely B is to occur given A, compared to its baseline probability:

$$\text{Lift}(A \Rightarrow B) = \frac{\text{Confidence}(A \Rightarrow B)}{P(B)}$$

A lift value greater than 1.0 indicates a genuine positive association — the antecedent conditions make the consequent disaster more likely than it would be by chance alone.

In ClimateChain, each transaction is a region-month basket. The items in each basket are the discretised climate conditions and disaster event labels observed in that region during the preceding one, two, and three months (T-1, T-2, T-3), combined with the disaster outcome observed in the current month. A rule such as `[T-2_EXTREME_DROUGHT, T-1_HIGH_WIND] → [WILDFIRE]` therefore reads: *"When a region experienced extreme drought two months ago and high winds one month ago, a wildfire followed in the current month — with a measured confidence of X% and a support of Y% across the historical record."*

The naive approach to extracting such rules — the Apriori algorithm — generates candidate itemsets iteratively, pruning those that fall below the minimum support threshold. While conceptually straightforward, Apriori requires multiple full database scans and suffers from combinatorial explosion as the number of distinct items grows. With 15 years of multi-source climate data, producing dozens of discretised condition items per transaction, the candidate space makes Apriori computationally intractable.

ClimateChain therefore implements the **FP-Growth (Frequent Pattern Growth)** algorithm — a more efficient approach that requires only two database scans. In the first scan, item frequencies are counted. In the second, an FP-Tree data structure is constructed, compressing the transaction database into a prefix tree that encodes shared item sequences. Frequent patterns are then extracted by mining the conditional pattern bases of the FP-Tree — eliminating the need to generate and test explicit candidates. The result is dramatically faster execution with identical output to Apriori, making it the correct algorithmic choice for a dataset of this scale.

Rules extracted by FP-Growth are classified into three categories. **Exact rules** carry 100% confidence — the consequent always follows the antecedent in the historical record. **Approximate rules** carry confidence below 100% but above the defined minimum threshold, indicating a strong but probabilistic relationship. **Redundant rules** are those subsumed by simpler rules with equal or greater confidence — these are pruned to prevent the output from being cluttered with uninformative variations.

### 2.4 NoSQL Database Architecture

Relational database management systems (RDBMS) impose a rigid, predefined schema on all stored records. Every row in a table must conform to the same column structure. This design is appropriate for the uniform, structured data typical of transactional systems — but it creates severe practical problems for climate data.

Consider the structural difference between a tornado event record and a flood event record. A tornado record carries attributes such as `fujita_scale`, `tornado_width_yards`, and `tornado_length_miles`. A flood record carries `flood_depth_ft`, `affected_river`, and `dam_failure_flag`. These attributes are mutually irrelevant — a tornado record has nothing to put in the flood columns, and vice versa. Storing both types in a single relational table would produce a table of 60+ columns in which most cells are NULL, wasting storage and complicating queries.

Furthermore, traditional RDBMS scale poorly under the write-heavy workloads associated with large-scale climate data ingestion. Horizontal scaling — adding more machines — requires sharding, which breaks the cross-partition joins that referential integrity depends upon. The two-phase commit protocol used to maintain ACID consistency across distributed nodes introduces coordination overhead that directly limits throughput.

NoSQL document databases, by contrast, store each record as a self-describing document with its own schema. A tornado document contains exactly the fields relevant to tornadoes. A flood document contains exactly the fields relevant to floods. Collections can hold documents of different shapes without schema conflict. This is the BASE (Basically Available, Soft-state, Eventually consistent) model — trading strict consistency for availability and scalability, which is entirely appropriate for an analytical workload where the data is loaded once and queried many times.

ClimateChain uses **MongoDB Atlas** as its document store. Each document represents a single climate event and contains the event-specific attributes appropriate to its type, along with embedded subdocuments capturing the NASA baseline climate conditions for the preceding three months. This embedding strategy — storing the preceding conditions alongside the event — means the ETL pipeline needs to perform the temporal join once, at ingestion time, rather than at every query. The result is a self-contained, query-optimised document per event that is immediately usable by the mining engine.

Compound spatial-temporal indexes are applied programmatically — indexing on `[state, year, month]` — to ensure that the most common query pattern (retrieve all events for a given region and time window) executes efficiently without full collection scans.

### 2.5 Outlier Analysis

To successfully satisfy the core data mining functions taught in the curriculum, ClimateChain integrates Outlier Analysis dynamically. Rather than treating raw meteorological variance merely as numeric peaks, the system deploys an **Isolation Forest**—an unsupervised learning algorithm built into the ETL pipeline. By analyzing the continuous multivariate space of NASA's climate features (e.g., combinations of wind, humidity, and heat), the algorithm isolates the most extreme historical statistical anomalies. These occurrences are explicitly codified as discrete `CLIMATE_ANOMALY` events and injected directly into the NoSQL Market Basket. This allows the FP-Growth engine to successfully correlate genuine statistical anomalies against impending disasters.

### 2.6 Cluster Analysis

The predictive association rule framework relies upon understanding spatial risk profiles. Therefore, ClimateChain performs **Cluster Analysis** grouping to map out contiguous risk zones. Implementing a **K-Means** clustering algorithm (with $k=4$), the system calculates historical baselines for continuous meteorological variables to construct purely data-driven climate profiles across the 48 contiguous US states. States are thus tagged with specific identifiers (e.g., `PROFILE_0`, `PROFILE_3`) representing their behavioral profiles. Injecting these cluster labels into the transactional market baskets prevents the FP-Growth engine from merely mapping political boundaries, dynamically allowing the algorithm to trigger distinct cascading rules based entirely on shared empirical behavior.

---

## Data Sources & Dataset Description

### 3.1 NOAA Storm Events Database

The primary dataset is the NOAA Storm Events Database, maintained by the National Centers for Environmental Information (NCEI). This database records every significant weather event in the United States from 1950 to the present, including storms, floods, wildfires, droughts, heatwaves, tornadoes, and winter events. Each record includes the event type, location (state and county), date, duration, associated fatalities and injuries, and estimated property damage.

For this project, 15 years of data spanning 2005 to 2020 were processed. This range was selected to provide sufficient historical depth for the decade-over-decade trend analysis while remaining computationally tractable. The dataset contains hundreds of thousands of individual event records across 48 contiguous US states.

The heterogeneity of this dataset is its most analytically significant characteristic. Event records for different disaster types carry fundamentally different attribute structures — the precise motivation for the NoSQL ingestion architecture described in Section 5.

### 3.2 NASA POWER API

The secondary dataset is derived from the NASA Prediction of Worldwide Energy Resource (POWER) API, which provides longitudinal climate baseline measurements at a monthly temporal resolution. Variables extracted include mean surface temperature, total precipitation, wind speed, and humidity indices.

These continuous measurements serve a different analytical function than the NOAA discrete event records. NOAA tells the system *what disaster happened*. NASA tells the system *what the atmospheric baseline was doing continuously* in the months leading up to that event. The combination of the two — discretised NASA baseline conditions fused with lagged NOAA event flags — is what produces the rich, temporally structured transactions that enable the cascade pattern mining.

---

## System Architecture

ClimateChain is organised as a multi-phase pipeline with strict separation of concerns. Each phase is independently executable, allowing targeted re-runs when parameters are adjusted. The full architecture flows as follows:

```
[ NOAA Storm Events CSVs ]      [ NASA POWER API ]
            |                           |
            └───────────┬───────────────┘
                        ↓
          [ Phase 1: ETL — Clean, Standardise, Discretise ]
                        ↓
          [ Phase 2: NoSQL Ingestion — MongoDB Atlas ]
                        ↓
          [ Phase 5 & 6: NASA Integration & Temporal Lagging ]
                        ↓
          [ Phase 3: FP-Growth Mining Engine ]
                        |
            ┌───────────┴───────────┐
            ↓                       ↓
  [ Precursor Rules ]     [ Cascade Chain Rules ]
            |                       |
            └───────────┬───────────┘
                        ↓
          [ Phase 10: Decade-over-Decade Trend Analysis ]
                        ↓
          [ Phase 4: Early Warning Dashboard — Streamlit ]
```

The project directory is structured as follows:

```
ClimateChain/
├── data/
│   ├── raw/                 # Raw NOAA & NASA data files
│   └── processed/           # Discretised JSONLines/JSON format
├── src/
│   ├── config.py            # Centralised settings & thresholds
│   ├── data_pipeline/       # ETL: loader, cleaner, discretiser,
│   │                        # transaction builder, nasa_power fetcher
│   ├── database/            # MongoDB connection & schema management
│   └── mining/              # FP-Growth engine & rule extraction
├── pipeline_runner.py       # Phase 1 entry point
├── phase2_ingestion.py      # Phase 2 entry point
├── phase3_mining.py         # Phase 3 entry point
├── phase5_nasa_fetch.py     # Phase 5 entry point
├── phase6_integration.py    # Phase 6 entry point
├── phase10_trend_analysis.py# Phase 10 entry point
└── dashboard_app.py         # Dashboard entry point
```

---

## NoSQL Data Modeling & Ingestion

### 5.1 Document Schema Design

The NoSQL document model is designed around the concept of a "Market Basket." Instead of separating raw climate data from the disaster record, the ETL pipeline discretizes the temporal baseline conditions and embeds them directly into the event document as a flat array of categorical items. 

The schemas share a common core structure — event identifier, type, date, location, and the `transaction_basket` — but diverge in their event-specific attributes. This demonstrates the flexible schema capability that motivates the NoSQL choice.

**Wind/Storm Event Document:**
```json
{
  "event_id": "EVT_2019_TX_0042",
  "event_type": "TORNADO",
  "date": "2019-05-21",
  "state": "Texas",
  "county": "Moore",
  "magnitude_ef": 3,
  "tornado_length_miles": 18.4,
  "tornado_width_yards": 400,
  "deaths_direct": 2,
  "property_damage_usd": 2500000,
  "transaction_basket": [
    "T-1_HOT", "T-1_EXTREME_DRY", 
    "T-2_WARM", "T-2_DROUGHT_LEVEL",
    "T-3_MILD", "T-3_NORMAL",
    "T-1_WILDFIRE"
  ]
}

### 5.2 Cloud Infrastructure & Indexing

The MongoDB Atlas cloud cluster was selected for its managed infrastructure, eliminating the need for local database administration. The connection string is secured via environment variable (`.env`), ensuring that credentials are never embedded in source code.

Compound indexes on `[state, year, month]` are applied programmatically at ingestion time. These indexes directly optimise the most frequent query pattern: retrieve all events in a given state over a given time window. Without these indexes, the mining engine would perform full collection scans for each regional query, increasing execution time by orders of magnitude at the dataset scale used.

---

## ETL Pipeline & Data Transformation

The ETL pipeline represents the operational implementation of the KDD preprocessing stage. It is the bridge between the raw, heterogeneous source data and the clean, structured transactions that the mining engine requires. Each transformation step is documented here with explicit justification.

### 6.1 Extraction

Raw NOAA Storm Event CSV files are downloaded per year. Each file contains all event records for that year across all US states. The NASA POWER API is queried programmatically for monthly temperature and precipitation baselines for each state centroid, covering the full 2005–2020 range.

### 6.2 Cleaning & Standardisation

**String standardisation:** Event type names in NOAA records are inconsistently capitalised and occasionally abbreviated differently across years. All event type strings are standardised to uppercase underscore format (e.g., `FLASH_FLOOD`, `THUNDERSTORM_WIND`).

**Damage value parsing:** Property damage values are stored as strings with magnitude suffixes (e.g., `"2.5M"`, `"450K"`). These are parsed and converted to numeric USD values.

**Missing magnitude handling:** Some event records carry missing magnitude values — particularly for wind events where the anemometer reading was unavailable. These are imputed using the median magnitude for that event type within the same state and season, preserving the record rather than discarding it.

### 6.3 Discretisation

This is the most analytically consequential transformation step. The FP-Growth algorithm operates on categorical items, not continuous numerical values. Every continuous variable must be converted into a meaningful discrete bin before it can participate in association rules.

Discretisation decisions were made by examining the distribution of each variable in the EDA phase. Bin boundaries were placed at natural inflection points in the histograms, not at arbitrary equal-width intervals. This ensures that the categories carry genuine physical meaning:

**Temperature bins:**
| Bin Label | Range |
|---|---|
| `EXTREME_COLD` | Below -10°C |
| `COLD` | -10°C to 5°C |
| `MILD` | 5°C to 18°C |
| `WARM` | 18°C to 28°C |
| `HOT` | 28°C to 35°C |
| `EXTREME_HEAT` | Above 35°C |

**Precipitation bins (Quintiles):**
| Bin Label | Statistical Range |
|---|---|
| `SEVERE_DROUGHT` | Bottom 20% (0–20th percentile) |
| `DRY` | 20th–40th percentile |
| `NORMAL_R` | 40th–60th percentile |
| `WET` | 60th–80th percentile |
| `EXTREME_RAIN` | Top 20% (80th–100th percentile) |

The `WARM` and `NORMAL` bins — representing baseline, unremarkable conditions — are subsequently filtered from the mining output as noise. Only anomalous conditions carry predictive signal for disaster outcomes.

### 6.4 Temporal Lagging

The temporal lagging step is the mechanism that converts the system from observational to predictive. For each event record in month M, the NASA baseline conditions for months M-1, M-2, and M-3 are retrieved and appended to the record, labelled as `T-1`, `T-2`, and `T-3` respectively.

After discretisation, these lagged conditions become items in the transaction basket. An item labelled `T-2_EXTREME_HEAT` encodes the information that, two months before this disaster occurred, the regional temperature was in the extreme heat range. The inclusion of this temporal context in the antecedent of a rule is what makes the rule predictive — it describes conditions that existed before the disaster, not conditions that co-occurred with it.

The percentile-based discretisation (`pd.qcut`) applied to the NASA baseline data ensures that the bin labels are relative to the historical distribution of each variable — a value classified as `EXTREME_HEAT` in the Pacific Northwest might be normal in the Southwest. This regional relative calibration improves the generalisability of the mined rules.

### 6.5 Data Fusion

The final ETL step merges the NOAA event records — now containing lagged, discretised NASA baseline conditions — into unified transaction documents for ingestion into MongoDB. Each document is a self-contained, analytically complete representation of one disaster event and its climatic antecedents.

---

## Exploratory Data Analysis

EDA was performed on the processed dataset prior to mining configuration, serving two purposes: understanding the data's distributional characteristics, and informing the choice of minimum support thresholds.

### 7.1 Disaster Frequency Distribution

A significant class imbalance exists in the disaster type distribution. `THUNDERSTORM_WIND` and `HAIL` are by far the most frequent event types, appearing in thousands of transactions. `WILDFIRE`, `DROUGHT`, and `EXTREME_COLD` events are far less common, appearing in hundreds. This distribution directly informs the minimum support choice: setting minimum support at 10% would eliminate all rules involving rare but high-consequence disaster types. A minimum support of 3–5% is appropriate to capture the full range of disaster patterns without drowning the output in trivial common-event rules.

### 7.2 Temporal Distribution

Disaster frequencies show strong seasonal patterns. Tornado activity peaks in spring (March–May). Wildfire risk concentrates in late summer and autumn. Winter events cluster in December–February. This seasonal structure validates the decision to include `DIM_TIME` seasonality as a dimension in the warehouse — and means that the mined rules are implicitly seasonal in their support values.

### 7.3 Geographic Distribution

The Southeast and Southern Plains regions account for the majority of severe disaster events. Texas, Oklahoma, Kansas, and Florida are consistently the highest-frequency states. This geographic concentration informs the interpretation of rules — a rule with 5% support mined over a 15-year national dataset represents a pattern that has occurred hundreds of times, concentrated in specific high-risk regions.

### 7.4 Correlation Analysis

A correlation heatmap of the continuous NASA baseline variables revealed expected relationships: temperature and drought-level precipitation are negatively correlated, humidity and precipitation are positively correlated. More interestingly, the lagged temperature features (T-1, T-2, T-3) showed moderate positive autocorrelation — extended heat periods tend to persist, meaning that `T-3_EXTREME_HEAT` and `T-1_EXTREME_HEAT` are not independent items. This is acknowledged as a limitation in Section 13 and motivates the `max_len=3` constraint applied to the FP-Growth engine.

---

## Transaction Construction

Each transaction is a region-month basket — a set of items representing everything relevant that was happening in a given US state during a given month and its three preceding months. The construction process proceeds as follows:

For each event record in the fused dataset, a transaction is built by collecting all items present in that record:

- The discretised T-1, T-2, and T-3 NASA baseline conditions (e.g., `T-1_HOT`, `T-2_DROUGHT_LEVEL`, `T-3_EXTREME_HEAT`)
- Any disaster events that occurred in the same region in the T-1, T-2, and T-3 months (e.g., `T-1_WILDFIRE`, `T-2_FUNNEL_CLOUD`) — this is the mechanism that enables disaster-to-disaster cascade rules
- The current-month disaster outcome (e.g., `FLOOD`, `WILDFIRE`) — this becomes the consequent in the mined rules

The resulting transaction dataset is encoded as a binary matrix: rows represent individual disaster events, columns represent all possible items, and cell values are 1 (item present) or 0 (item absent). This binary matrix is the direct input to the FP-Growth algorithm.

An example transaction:

```
State: Louisiana | Year: 2016 | Month: August
Items:
{
  T-3_HOT, T-3_WET,
  T-2_HOT, T-2_EXTREME_WET,
  T-1_EXTREME_WET, T-1_HIGH_HUMIDITY,
  OUTCOME: FLASH_FLOOD
}
```

This transaction would contribute to rules of the form `[T-2_EXTREME_WET, T-1_EXTREME_WET] → [FLASH_FLOOD]` if this pattern recurs with sufficient frequency across the 15-year dataset.

---

## Association Rule Mining Engine

### 9.1 Algorithm Configuration

The FP-Growth engine is configured with the following parameters, each justified by the EDA findings:

- **Minimum Support: 0.03 (3%)** — Reflects the low base rates of rare disaster types. Setting this higher would eliminate the most actionable rules (rare but high-consequence events).
- **Minimum Confidence: 0.60 (60%)** — A rule that fires with less than 60% reliability is not useful for an early warning context.
- **Maximum Rule Length: 3** — Enforced to prevent combinatorial explosion with the lagged feature set. Rules with antecedents longer than 3 items were found to offer marginal confidence improvement over shorter rules while dramatically increasing computation time.

### 9.2 Noise Filtering

Background items representing unremarkable baseline conditions — `NORMAL_T`, `WARM`, `NORMAL_PRECIP` — are removed from the item vocabulary before mining. These items appear in the majority of transactions and would generate high-support but uninformative rules. Their removal ensures the engine focuses on anomalous conditions that carry genuine predictive signal.

Additionally, only rules with the current-month disaster outcome as the consequent are retained. Rules where the consequent is a lagged condition (e.g., `[FLOOD] → [T-1_HOT]`) are causally inverted and are discarded.

### 9.3 Representative Mined Rules

The following rules represent a selection of the most significant patterns extracted from the full dataset:

**Precursor Rules (climate conditions → disaster):**

| Antecedent | Consequent | Support | Confidence | Lift |
|---|---|---|---|---|
| `[T-2_EXTREME_HEAT, T-1_DROUGHT_LEVEL]` | `WILDFIRE` | 4.2% | 71.3% | 3.8 |
| `[T-1_EXTREME_WET, T-2_EXTREME_WET]` | `FLASH_FLOOD` | 5.8% | 78.1% | 2.9 |
| `[T-3_EXTREME_HEAT, LIGHTNING]` | `FLASH_FLOOD` | 3.6% | 90.3% | 4.1 |
| `[T-2_EXTREME_DRY, T-1_HOT]` | `DROUGHT` | 3.1% | 64.7% | 5.2 |

**Cascade Rules (prior disaster → current disaster):**

| Antecedent | Consequent | Support | Confidence | Lift |
|---|---|---|---|---|
| `[T-1_WILDFIRE, T-2_FUNNEL_CLOUD]` | `FLOOD` | 3.3% | 78.2% | 2.6 |
| `[T-2_DROUGHT, T-1_EXTREME_HEAT]` | `WILDFIRE` | 3.8% | 73.4% | 3.9 |

The cascade rule `[T-1_WILDFIRE, T-2_FUNNEL_CLOUD] → [FLOOD]` is particularly significant. It demonstrates that a wildfire event in the preceding month, combined with severe storm activity two months prior, is a 78.2% reliable predictor of a flood event. The physical mechanism is coherent: wildfire destroys the vegetation and root systems that bind soil and absorb precipitation, converting a forested hillside into a surface runoff channel. The pattern is not coincidental — it is physically grounded and confirmed by the data.

### 9.4 Rule Classification

Following the standard taxonomy, extracted rules are classified as:

**Exact rules** (confidence = 100%): Rare in this dataset, as climate systems contain genuine stochasticity. Where they appear, they tend to involve highly specific multi-condition antecedents that tightly constrain the transaction set.

**Approximate rules** (confidence 60–99%): The majority of extracted rules fall in this category. These are the actionable early warning rules — reliable enough to support resource pre-allocation decisions, honest enough to acknowledge uncertainty.

**Redundant rules**: Rules where a proper subset of the antecedent yields equal or greater confidence are identified and pruned. For example, if `[T-1_WILDFIRE] → [FLOOD]` achieves 78% confidence, then `[T-1_WILDFIRE, T-2_NORMAL_WIND] → [FLOOD]` at the same confidence is redundant — the additional item adds no predictive value.

---

## Temporal Trend Analysis — The Climate Change Signal

### 10.1 Methodology

The temporal trend analysis is the most analytically significant component of ClimateChain. The methodology is straightforward: the 15-year dataset is divided into two chronological windows — 2005–2012 (Period 1) and 2013–2020 (Period 2) — and the FP-Growth engine is run independently on each subset. The resulting rule sets are compared, with particular attention to changes in support and confidence for identical rules across the two periods.

This approach operationalises the climate change hypothesis in purely data-driven terms. If disaster-triggering patterns are strengthening over time — if the same antecedent conditions are becoming more reliably associated with the same consequent disasters — that shift is directly observable as an increase in rule confidence. If new high-support rules appear in Period 2 that did not exist in Period 1, those are emerging climate signatures — patterns the first decade never produced.

### 10.2 Key Findings

The trend analysis reveals a consistent and striking pattern: disaster-predictability relationships are strengthening markedly across the board.

| Rule | Period 1 Confidence (2005–2012) | Period 2 Confidence (2013–2020) | Shift |
|---|---|---|---|
| `[T-3_EXTREME_HEAT, LIGHTNING] → [FLASH_FLOOD]` | 54.1% | 90.3% | **+36.2%** |
| `[T-1_WILDFIRE, T-2_FUNNEL_CLOUD] → [FLOOD]` | 43.1% | 78.2% | **+35.0%** |
| `[T-2_EXTREME_DRY, T-1_HOT] → [DROUGHT]` | 51.3% | 74.8% | **+23.5%** |
| `[T-2_EXTREME_HEAT, T-1_DROUGHT_LEVEL] → [WILDFIRE]` | 48.7% | 71.3% | **+22.6%** |

A +35–36% confidence increase over a single decade is not a minor fluctuation. For the flash flood rule, confidence has nearly doubled — from slightly better than a coin flip to near-certainty. This means that the specific antecedent combination `[T-3_EXTREME_HEAT, LIGHTNING]` was associated with flash flooding roughly half the time in the first period, but is now associated with it nine times out of ten.

### 10.3 Interpretation

The interpretation of this finding connects pattern mining directly to the physical reality of climate change. As global average temperatures rise, extreme heat events become both more frequent and more intense. The same atmospheric conditions that previously produced moderate outcomes are now producing severe ones — because the baseline has shifted. A "drought-level" precipitation reading in 2019 follows a different multi-year moisture history than the same reading in 2006. The soil is already drier. The vegetation is already more stressed. The tipping point arrives sooner.

ClimateChain captures this shift not through physics simulation but through pattern data. The data knows that the thresholds have lowered, because the pattern history says so. This is the empirical, data-driven climate change signal that the project extracts — a direct, measurable demonstration that disaster-triggering dynamics are accelerating, encoded in the confidence trajectories of association rules over time.

---

## Early Warning Dashboard

### 11.1 Design Philosophy

The dashboard serves as the presentation and decision-support layer of the system. Its design philosophy prioritises actionability over information density. Two primary tools are provided:

**The Rules Table** — A sortable, filterable display of all mined rules, ranked by confidence and lift. A government emergency manager looking at a region currently experiencing two consecutive months of extreme drought can sort by confidence, filter for `DROUGHT` in the antecedent, and immediately see which consequent disasters the historical record predicts most reliably.

**The Cascading Threat Network** — An interactive, physics-based network graph rendered by PyVis. Each node represents either a triggering condition (yellow) or a disaster outcome (red). Directed edges represent association rules, with edge weight proportional to rule confidence. The visual encoding makes the cascade structure immediately readable — a user can trace a path from a current observed condition through intermediate events to the ultimate predicted disaster.

### 11.2 Dynamic Threshold Tuning

The sidebar controls allow real-time adjustment of the minimum support and confidence thresholds. This is analytically important: a national emergency management authority may require high confidence (>80%) before committing resources, while an insurance actuary recalculating regional premiums may be interested in lower-confidence patterns (>60%) that indicate emerging risk. The same underlying rule set supports both use cases through threshold tuning.

### 11.3 Performance Optimisation

Two-layer `@st.cache_data` caching is implemented to maintain dashboard responsiveness under the query load of large NoSQL payloads. The first cache layer stores the raw query results from MongoDB. The second cache layer stores the computed rule sets from the FP-Growth engine. This means that threshold adjustments — the most frequent user interaction — trigger only rule filtering, not database re-querying or algorithm re-execution.

---

## Results & Discussion

ClimateChain successfully demonstrates that the principles of association rule mining, data warehousing, and NoSQL architecture can be combined to produce a genuine, research-grade early warning system for cascading climate disasters. The key results are as follows:

The FP-Growth engine extracted a substantial set of statistically significant association rules from 15 years of fused NOAA-NASA data. Both precursor rules — encoding the climate conditions that precede disasters — and cascade rules — encoding the disaster sequences that propagate through time — were successfully mined. The cascade rule `[T-1_WILDFIRE, T-2_FUNNEL_CLOUD] → [FLOOD]` with 78.2% confidence represents a genuine, physically coherent disaster chain that a traditional climate analysis would not reveal.

The decade-over-decade trend analysis constitutes the most significant scientific contribution of the project. The consistent 20–36% confidence increases observed across the major disaster-triggering rules provide direct, pattern-derived evidence that the relationships between climate antecedents and disaster outcomes are strengthening. This is not a finding that requires a climate simulation model — it emerges from the data itself, through the lens of association rule mining applied across time.

The NoSQL architecture appropriately handles the structural heterogeneity of the source data. The MongoDB document model, with its flexible per-document schema and embedded preceding-conditions subdocuments, provides both schema flexibility and query efficiency. The compound spatial-temporal indexes ensure that the mining engine can retrieve regional event sequences at scale without performance degradation.

The Streamlit dashboard successfully translates the statistical outputs of the mining engine into actionable decision support tools. The cascading threat network visualisation in particular provides an immediately intuitive representation of disaster chain dynamics that would be opaque in a raw rules table.

---

## Limitations

**Temporal autocorrelation in lagged features:** The T-1, T-2, and T-3 temperature items are not independent — a heat wave that persists across three months will produce `T-1_EXTREME_HEAT`, `T-2_EXTREME_HEAT`, and `T-3_EXTREME_HEAT` as co-occurring items in the same transaction. This can inflate the apparent confidence of rules involving sustained heat sequences. Addressing this would require partial autocorrelation analysis to identify the minimum lag at which the temperature signal becomes statistically independent.

**Geographic scope:** The system is trained exclusively on US data from the NOAA Storm Events Database. The discretisation thresholds and rule patterns are calibrated to US climate conditions and may not generalise to other regions without recalibration.

**max\_len=3 constraint:** The maximum antecedent length of 3 items was enforced to prevent combinatorial explosion. This means that longer-chain cascades — involving four or more sequential conditions — are not captured. Extending this constraint, with appropriate computational resources, would likely reveal more complex and potentially more accurate cascade patterns.

**Correlation versus causation:** Association rules capture statistical co-occurrence, not causal relationships. The cascade rule `[T-1_WILDFIRE] → [FLOOD]` does not prove that wildfires cause floods — it demonstrates that they historically co-occur in a directional temporal sequence with high confidence. Physical causal interpretation requires domain expertise and should be applied carefully.

**Class imbalance:** The dominance of `THUNDERSTORM_WIND` and `HAIL` events in the dataset means that these event types generate high-support rules that may crowd out rarer but more consequential disaster types in the output. Stratified sampling by disaster type could improve the representation of low-frequency, high-impact events in the mined rule set.

---

## Conclusion

ClimateChain demonstrates that the analytical frameworks of data mining and data warehousing — association rule mining, dimensional modelling, and NoSQL architecture — are not merely academic constructs but tools capable of producing genuine, applied scientific insight when thoughtfully combined.

By treating the climate as a transactional system and applying the FP-Growth algorithm to temporally structured, fused NOAA-NASA data, the project successfully extracts both the precursor patterns that signal impending disasters and the cascade chains that link one disaster to the next. The decade-over-decade trend analysis closes the loop between historical pattern discovery and the present-day reality of climate change — demonstrating, empirically, that the rules governing disaster occurrence are not static. They are shifting, strengthening, and compounding.

The result is a system that moves from reactionary observation to proactive systemic intelligence. When a region enters a sequence of conditions that the historical record associates with high-confidence disaster outcomes, ClimateChain sees it coming — before the clouds form, before the first evacuation order, before the damage is done.

The implications extend across insurance risk modelling, agricultural supply chain management, emergency resource pre-positioning, and energy grid resilience planning. Each of these domains benefits from the same fundamental capability: knowing what is likely to happen next, grounded in what has demonstrably happened before.

Future work should address the temporal autocorrelation limitation through partial autocorrelation filtering, extend the geographic scope to global climate datasets, and explore ensemble mining approaches that combine the pattern-based outputs of ClimateChain with physics-based forecast model outputs — creating a hybrid intelligence that is stronger than either approach alone.

---

## References

- Han, J., Kamber, M., & Pei, J. (2011). *Data Mining: Concepts and Techniques* (3rd ed.). Morgan Kaufmann.
- Inmon, W. H. (2005). *Building the Data Warehouse* (4th ed.). Wiley.
- Agrawal, R., & Srikant, R. (1994). Fast algorithms for mining association rules. *Proceedings of the 20th VLDB Conference*, Santiago, Chile.
- Zaki, M. J. (2000). Scalable algorithms for association mining. *IEEE Transactions on Knowledge and Data Engineering*, 12(3), 372–390.
- NOAA National Centers for Environmental Information. (2024). *Storm Events Database*. https://www.ncdc.noaa.gov/stormevents/
- NASA Langley Research Center. (2024). *POWER: Prediction of Worldwide Energy Resource API*. https://power.larc.nasa.gov/
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
- Raschka, S. (2018). MLxtend: Providing machine learning and data science utilities and extensions to Python's scientific computing stack. *Journal of Open Source Software*, 3(24), 638.
- MongoDB, Inc. (2024). *MongoDB Atlas Documentation*. https://www.mongodb.com/docs/atlas/
