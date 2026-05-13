# Session 3 — CRISP-DM Data Preparation Tasks

## How to claim a task

1. Open `session-3/task-ownership.yaml`
2. Find an unclaimed task (no `owner` field)
3. Add your name, today's date, status `claimed`
4. Push — you own it, no one else will touch it
5. When done, set status to `done` and push

> Only Rafik can release a claimed task.

---

## PROCESS track — retrofit existing notebooks

These tasks fix the existing notebooks to visibly show the CRISP-DM data preparation process.
The teacher's feedback: the work is done but the process isn't documented.

### P1 — Retrofit notebook 02 (grid-trees)
**File:** `notebooks/02-grid-trees.ipynb`
**What to do:**
- Print row count before and after every filter
- Add a markdown cell above each filter explaining the design decision (why these rows, why this threshold)
- Add bounds assertions: tree height, crown diameter, coordinate ranges for Barcelona
- Document unit choices (metres? degrees?)
- Show a before/after sample of the dataframe

### P2 — Retrofit notebook 03 (scoring)
**File:** `notebooks/03-scoring.ipynb`
**What to do:**
- Print row count before and after every transformation
- Add markdown cells explaining each scoring weight decision (why this weight, not another)
- Add bounds assertions on output scores (should be 0–1 or 0–100 — assert this)
- Show drop/impute/flag decisions for any missing values
- Document unit standardisation (NDVI is unitless, LST in Celsius — confirm this is stated)

### P3 — Retrofit notebook 04 (connectivity)
**File:** `notebooks/04-connectivity.ipynb`
**What to do:**
- Print node/edge counts before and after every filter
- Explain the design decision for distance thresholds (why X metres for connectivity?)
- Add bounds assertions on network metrics
- Flag any islands/disconnected components explicitly

### P4 — Retrofit notebook 05 (visualisation)
**File:** `notebooks/05-visualisation.ipynb`
**What to do:**
- Add a markdown intro cell explaining what the map shows and what data feeds it
- Document the colour scale choices (what does red vs green mean, what are the thresholds)
- Add a data provenance section at the top (where did each layer come from)

### P5 — Defensive bounds layer for core pipeline
**File:** `notebooks/03-scoring.ipynb` or new `notebooks/00-data-validation.ipynb`
**What to do:**
- Write assertions for all key columns following the class example:
  - NDVI: -1 to 1
  - LST (land surface temp): reasonable Barcelona range (e.g. 15–55°C in summer)
  - Sealed surface %: 0–100
  - Coordinates: Barcelona bounding box
- Print a validation report: how many rows passed, how many flagged

---

## DATA track — each person adds their own data layer

The teacher wants each team member to contribute their own dataset with their own
documented preparation process. Full CRISP-DM notebook required for each.

### D1 — Add a new data layer: your choice
**Who:** Any team member (Dominika / Juan)
**What to do:**
- Pick a dataset that strengthens the project narrative
  - Ideas: pedestrian foot traffic, green space access, biodiversity records, soil type, noise/air quality, demographics
- Download or source it
- Write a full notebook (`notebooks/0X-[your-layer].ipynb`) showing:
  - Raw data load + row/column counts
  - Design decisions: which rows belong, which columns matter
  - Cleaning steps with before/after prints
  - Unit standardisation
  - Bounds assertions
  - Final export to `data/[your-layer].geojson` or equivalent
- Write a datasheet in `docs/datasheets/[your-layer].md`

### D2 — Add a second new data layer: your choice
**Who:** Any team member (Dominika / Juan — whoever didn't do D1)
**Same requirements as D1.**

### D3 — Document Said's existing data preparation process
**Who:** Anyone
**File:** new `notebooks/00-data-provenance.ipynb`
**What to do:**
- Walk through all datasets in `data/` and for each one document:
  - Where it came from (source URL, date downloaded)
  - What cleaning was applied (even if just "used as-is")
  - What the key columns are and their units
  - Any known gaps or caveats
- This notebook becomes the "data contract" the teacher wants to see

---

## DOCS track — structure and documentation

### DO1 — Write the Session 3 README
**File:** `session-3/README.md`
**What to do:**
- Follow the course session 3 template structure
- Summarise what data preparation decisions were made for this project
- Link to each notebook
- Should be navigable by the teacher without running code

### DO2 — Update data-quality-audit to show CRISP-DM framing
**File:** `docs/data-quality-audit.md`
**What to do:**
- Restructure sections to match CRISP-DM language: Select → Clean → Construct → Integrate → Format
- For each dataset, explicitly state the drop/impute/flag/model decisions made
- Add a "design decisions" subsection for each dataset
