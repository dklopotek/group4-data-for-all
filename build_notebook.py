"""Construct and execute notebooks/01-data-profiling.ipynb."""
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from pathlib import Path
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

nb = new_notebook()
cells = []

cells.append(new_markdown_cell("""\
# Data Profiling — Ajuntament Barcelona Tree Inventory

**Purpose:** describe the dataset's shape, distributions, gaps, and anomalies
so we know what we have before building any pipeline on it.

**Input:** `data/arbrat-viari.csv` (street trees) + `data/arbrat-zona.csv`
(park trees), Open Data BCN, 2024-Q4 / 2026-Q1 vintage.

**Output:** findings written into `docs/data-quality-audit.md`, plus
`data/profile-summary.json` machine-readable summary.

**Decision unit reference:** Superilla / 400m grid. The 2x rule requires
data <=200m native — per-tree point coordinates pass trivially.
"""))

cells.append(new_code_cell("""\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 100)
sns.set_theme(style="whitegrid")
"""))

cells.append(new_markdown_cell("""\
## Cell 3 — Load & combine

The Ajuntament publishes street and park tree inventories as separate CSV
files. We tag each with a `source` column and concatenate."""))

cells.append(new_code_cell("""\
viari = pd.read_csv("data/arbrat-viari.csv", encoding="utf-8", low_memory=False)
zona = pd.read_csv("data/arbrat-zona.csv", encoding="utf-8", low_memory=False)
viari["source"] = "street"
zona["source"] = "park"
df = pd.concat([viari, zona], ignore_index=True)
print(f"Street trees: {len(viari):>7,}")
print(f"Park trees:   {len(zona):>7,}")
print(f"Combined:     {len(df):>7,}  ({len(df.columns)} cols)")
df.head(3)
"""))

cells.append(new_markdown_cell("## Cell 4 — Shape & dtypes"))

cells.append(new_code_cell("""\
print(f"Rows: {df.shape[0]:,}")
print(f"Cols: {df.shape[1]}")
print()
print(df.dtypes)
"""))

cells.append(new_markdown_cell("""\
## Cell 5 — Missing values

Anything above 20% deserves a note in the audit; anything above 80% is
essentially absent."""))

cells.append(new_code_cell("""\
missing = df.isna().mean().sort_values(ascending=False)
missing_pct = (missing * 100).round(2)
missing_pct[missing_pct > 0]
"""))

cells.append(new_markdown_cell("## Cell 6 — Coordinate bounds & district coverage"))

cells.append(new_code_cell("""\
print(f"Lat range: {df['latitud'].min():.6f}  ->  {df['latitud'].max():.6f}")
print(f"Lon range: {df['longitud'].min():.6f}  ->  {df['longitud'].max():.6f}")
print()
print("Trees per district:")
print(df["nom_districte"].value_counts().to_string())
"""))

cells.append(new_markdown_cell("""\
## Cell 7 — Categorical / ID summary

Low-cardinality fields are useful for filtering; high-cardinality fields
(species name) drive the FungalRoot join."""))

cells.append(new_code_cell("""\
for col in ["tipus_element", "categoria_arbrat", "tipus_aigua", "tipus_reg",
            "codi_districte", "cat_nom_cientific", "cat_especie_id"]:
    n = df[col].nunique(dropna=True)
    print(f"  {col:25s}  {n:>5} unique")
"""))

cells.append(new_markdown_cell("""\
## Cell 8 — Species: how many distinct species, and is the taxonomy
consistent enough to join against FungalRoot at species level?

This is the v1 brief's open question. We test for "genus-only" entries
(species names that are just a genus, e.g. *Washingtonia sp*) — if the
fraction is high, we'd have to fall back to genus-level matching."""))

cells.append(new_code_cell("""\
def is_genus_only(name):
    if not isinstance(name, str): return None
    n = name.strip()
    if " sp." in n or n.endswith(" sp"): return True
    parts = n.replace("×", " ").split()
    parts = [p for p in parts if p and p != "x" and p != "×"]
    return len(parts) < 2

df["_genus_only"] = df["cat_nom_cientific"].apply(is_genus_only)
total = df["cat_nom_cientific"].notna().sum()
n_genus = int(df["_genus_only"].sum())
n_missing = int(df["cat_nom_cientific"].isna().sum())
print(f"Total non-null species names:  {total:,}")
print(f"Genus-only entries:            {n_genus:,}  ({n_genus/total*100:.2f}%)")
print(f"Missing species names:         {n_missing:,}")
print()
print("Genus-only examples (top 10):")
print(df[df["_genus_only"]==True]["cat_nom_cientific"].value_counts().head(10).to_string())
"""))

cells.append(new_markdown_cell("""\
## Cell 9 — Top species composition

Are most trees AM-host genera (*Platanus*, *Tilia*, *Celtis*, *Citrus*,
*Melia*) — in which case AM-blindness is a major limit on what GBIF can
tell us — or do EM-host genera (*Quercus*, *Pinus*) provide a meaningful
subset where the observation layer can do useful work?"""))

cells.append(new_code_cell("""\
top20 = df["cat_nom_cientific"].value_counts().head(20)
top20
"""))

cells.append(new_code_cell("""\
fig, ax = plt.subplots(figsize=(10, 7))
top20[::-1].plot(kind="barh", ax=ax, color="#3a7d44")
ax.set_xlabel("Tree count")
ax.set_title("Top 20 species in Barcelona's public-realm tree inventory")
plt.tight_layout()
plt.show()
"""))

cells.append(new_markdown_cell("""\
## Cell 10 — Planting date completeness + temporal coverage

How much of the inventory has a known planting date? What's the span?
Anomalies (future dates, pre-1900) flagged."""))

cells.append(new_code_cell("""\
df["data_plantacio_dt"] = pd.to_datetime(df["data_plantacio"], errors="coerce")
total_pd = df["data_plantacio"].notna().sum()
valid_pd = df["data_plantacio_dt"].notna().sum()
missing_pd = df["data_plantacio"].isna().sum()
print(f"Records WITH planting date string:    {total_pd:,}")
print(f"  parseable as date:                  {valid_pd:,}")
print(f"  unparseable (kept null):            {total_pd - valid_pd:,}")
print(f"Records WITHOUT planting date string: {missing_pd:,}  ({missing_pd/len(df)*100:.1f}%)")
known = df["data_plantacio_dt"].dropna()
if len(known):
    print(f"Date range (parsed):  {known.min()}  ->  {known.max()}")
    future = (df["data_plantacio_dt"] > pd.Timestamp.now()).sum()
    pre_1900 = ((df["data_plantacio_dt"] < pd.Timestamp("1900-01-01"))
                & df["data_plantacio_dt"].notna()).sum()
    print(f"  Future-dated entries:   {int(future)}")
    print(f"  Pre-1900 entries:       {int(pre_1900)}")
"""))

cells.append(new_markdown_cell("""\
## Cell 11 — Tree count by district"""))

cells.append(new_code_cell("""\
fig, ax = plt.subplots(figsize=(10, 6))
counts = df["nom_districte"].value_counts()
counts.plot(kind="bar", ax=ax, color="#3a7d44")
ax.set_ylabel("Tree count")
ax.set_title("Tree inventory size by district (BCN)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()
"""))

cells.append(new_markdown_cell("## Cell 12 — Anomaly hunt"))

cells.append(new_code_cell("""\
anomalies = []

bbox_oob = df[((df["latitud"] < 41.30) | (df["latitud"] > 41.50) |
               (df["longitud"] < 2.04) | (df["longitud"] > 2.24)) &
              df["latitud"].notna()]
anomalies.append(("coords outside BCN bbox", len(bbox_oob)))

bad_dist = df[df["codi_districte"].isna() | (df["codi_districte"].astype(str) == "99")]
anomalies.append(("missing/invalid district", len(bad_dist)))

anomalies.append(("duplicate codi", int(df["codi"].duplicated().sum())))

bad_id = df[(df["cat_especie_id"].astype(str).str.isnumeric()) &
            (pd.to_numeric(df["cat_especie_id"], errors="coerce") <= 0)]
anomalies.append(("species_id <= 0", len(bad_id)))

future = (df["data_plantacio_dt"] > pd.Timestamp.now()).sum()
anomalies.append(("future plantation dates", int(future)))

pre1900 = ((df["data_plantacio_dt"] < pd.Timestamp("1900-01-01"))
           & df["data_plantacio_dt"].notna()).sum()
anomalies.append(("pre-1900 plantation dates", int(pre1900)))

anom_df = pd.DataFrame(anomalies, columns=["anomaly", "count"])
print(anom_df.to_string(index=False))
"""))

cells.append(new_markdown_cell("""\
## Cell 13 — Three things profiling revealed

1. **Species-level taxonomy is consistent.** Only ~25 records (0.01%) are
   genus-only — all *Washingtonia sp*. The v1 brief's worry that we'd be
   forced to fall back to genus-level FungalRoot matching is unfounded;
   species-level join is feasible.

2. **AM-host dominance confirmed empirically.** The top six species
   (*Platanus x acerifolia*, *Celtis australis*, *Tipuana tipu*,
   *Styphnolobium japonicum*, *Melia azedarach*, *Brachychiton populneus*)
   are AM hosts. EM-host taxa (*Pinus pinea*, *Pinus halepensis*,
   *Quercus ilex*, ~9k trees combined) appear at meaningful counts so
   the observed layer can still do useful work for the EM-dominant
   subset, but the dominant signal is AM and therefore not
   citizen-science-visible — the AM-blindness limit is foundational, not
   a footnote.

3. **Planting dates are mostly missing.** ~81% of records carry no
   planting date. Snapshot-state analysis only; do not attempt
   change-detection without comparing two snapshots.

**Implications for the brief:** v1 brief's "consistent species-level
taxonomy" open question is **resolved YES**. v2 brief is updated to
reflect.

**Implications for the pipeline (Session 3):** species-level FungalRoot
join is feasible; treat genus-only entries (~25) as a documented dropout.
Planting-date analyses are out of scope at inventory level.
"""))

cells.append(new_markdown_cell("## Cell 14 — Save profile summary"))

cells.append(new_code_cell("""\
profile_summary = {
    "dataset": "Ajuntament BCN tree inventory (street + park combined)",
    "rows_street": int(len(viari)),
    "rows_park": int(len(zona)),
    "rows_combined": int(len(df)),
    "columns": int(len(df.columns)),
    "missing_pct": {col: float(frac) for col, frac in missing.items() if frac > 0},
    "coord_bounds": {
        "lat_min": float(df["latitud"].min()),
        "lat_max": float(df["latitud"].max()),
        "lon_min": float(df["longitud"].min()),
        "lon_max": float(df["longitud"].max()),
    },
    "unique_species": int(df["cat_nom_cientific"].nunique()),
    "unique_districts": int(df["nom_districte"].nunique()),
    "trees_per_district": df["nom_districte"].value_counts().to_dict(),
    "top_20_species": top20.to_dict(),
    "genus_only_count": int(n_genus),
    "genus_only_pct": float(n_genus / total * 100),
    "anomalies": dict(anomalies),
    "planting_date_missing_pct": float(df["data_plantacio"].isna().mean()),
}
with open("data/profile-summary.json", "w", encoding="utf-8") as f:
    json.dump(profile_summary, f, indent=2, default=str, ensure_ascii=False)
print("Saved data/profile-summary.json")
"""))

nb["cells"] = cells
Path("notebooks").mkdir(exist_ok=True)
nb_path = "notebooks/01-data-profiling.ipynb"
with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print(f"Wrote unexecuted notebook: {nb_path}")

print("Executing notebook...")
from nbconvert.preprocessors import ExecutePreprocessor
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

with open(nb_path, "r", encoding="utf-8") as f:
    nb_loaded = nbf.read(f, as_version=4)

ep.preprocess(nb_loaded, {"metadata": {"path": "."}})

with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb_loaded, f)

n_code = sum(1 for c in nb_loaded.cells if c.cell_type == "code")
n_with_output = sum(1 for c in nb_loaded.cells if c.cell_type == "code" and c.get("outputs"))
print(f"Executed notebook: {n_code} code cells, {n_with_output} with outputs")
