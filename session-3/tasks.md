# Session 3 — CRISP-DM Data Preparation Tasks

> **Scope:** Data pipeline strategy only. No frontend, no map UI, no visualisation improvements.
> The teacher will not review any frontend work. Focus: how data is processed, why, and for whom.

> Claim a task in `session-3/task-ownership.yaml` before starting.
> Only Rafik can release a claimed task.

---

## PROCESS — retrofit existing notebooks to show CRISP-DM process

The teacher's core feedback: the work is done but the process isn't documented.
Each notebook needs: before/after row counts, design decision cells, bounds assertions.

### P1 — Retrofit notebook 02 (grid-trees)
**File:** `notebooks/02-grid-trees.ipynb`
- Print row count before and after every filter
- Add markdown cell above each filter explaining the design decision
- Add bounds assertions: tree height, crown diameter, Barcelona coordinate range
- Show a before/after sample of the dataframe

### P2 — Retrofit notebook 03 (scoring)
**File:** `notebooks/03-scoring.ipynb`
- Print row count before and after every transformation
- Add markdown cells explaining each scoring weight decision
- Add bounds assertions on output scores (0–1 range — assert this)
- Show drop/impute/flag decisions for any missing values
- State units explicitly: NDVI is unitless, LST in Celsius

### P3 — Retrofit notebook 04 (connectivity)
**File:** `notebooks/04-connectivity.ipynb`
- Print node/edge counts before and after every filter
- Explain the design decision for distance thresholds
- Add bounds assertions on network metrics
- Flag disconnected components explicitly

### P4 — Retrofit notebook 05 (visualisation)
**File:** `notebooks/05-visualisation.ipynb`
- Add intro markdown cell: what the map shows, what data feeds it
- Document colour scale choices and thresholds
- Add a data provenance section at the top

### P5 — Defensive bounds validation layer
**File:** new `notebooks/00-data-validation.ipynb`
- Assert all key columns are in range:
  - NDVI: −1 to 1
  - LST (land surface temp): 15–55 °C for Barcelona summer
  - Sealed surface %: 0–100
  - Coordinates: Barcelona bounding box
- Print a validation report: rows passed vs flagged

---

## DATA — personal data layers

Each person adds their own dataset with a full CRISP-DM notebook.
These tasks are pre-assigned — see task-ownership.yaml.

### D-DOMINIKA — Dominika's data layer
- Pick a dataset that strengthens the project (weather, soil, noise, biodiversity, demographics…)
- Full notebook: raw load → design decisions → cleaning → bounds → export
- Export to `data/[layer-name].geojson` or equivalent
- Write datasheet in `docs/datasheets/[layer-name].md`

### D-JUAN — Juan's data layer
- Same requirements as D-DOMINIKA
- Different dataset from Dominika's

---

## DOCS — structure and framing

### DO1 — Write the Session 3 README
**File:** `session-3/README.md`
- Follow the course session 3 template structure
- Summarise data preparation decisions made for this project
- Link to each notebook
- Must be navigable by the teacher without running code

### DO2 — Restructure data-quality-audit with CRISP-DM framing
**File:** `docs/data-quality-audit.md`
- Restructure sections: Select → Clean → Construct → Integrate → Format
- For each dataset: explicitly state drop/impute/flag/model decisions
- Add a "design decisions" subsection per dataset
