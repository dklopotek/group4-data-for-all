"""
analyze_pipeline.py — Analyse the Mycorrhizal Barcelona pipeline output.

Usage: python outputs/analyze_pipeline.py
"""

import sys
import json
import geopandas as gpd
import pandas as pd
import numpy as np

# ── Load the scored grid ─────────────────────────────────────────────────────
print("Loading scored_grid.geojson...", file=sys.stderr)
gdf = gpd.read_file("data/processed/scored_grid.geojson")

# Drop geometry for tabular analysis
df = pd.DataFrame(gdf.drop(columns="geometry", errors="ignore"))

print("=" * 70)
print("MYCORRHIZAL BARCELONA — Pipeline Output Analysis")
print("=" * 70)

# ── 1. BASIC STATS ───────────────────────────────────────────────────────────
print("\n## 1. Dataset Overview")
print(f"  Cells: {len(df)}")
print(f"  Columns: {len(df.columns)}")
print(f"  Districts represented: {df['district'].nunique()} / 10")

n_districts = df["district"].nunique()
print(f"  Districts represented: {n_districts} / 10")
present = sorted(df["district"].dropna().unique())
print(f"  Districts: {present}")

# ── 2. TOP 15 PRIORITY CELLS ────────────────────────────────────────────────
print("\n## 2. Top 15 Priority Cells (Scenario B — Sealed-Dominant)")
print(f"  {'#':>3s}  {'Cell ID':>10s}  {'District':<25s}  {'Score_B':>7s}  "
      f"{'Intervention':<17s}  {'S1(sld)':>7s}  {'S2(lst)':>7s}  "
      f"{'S3(ndvi)':>8s}  {'S4(mm)':>6s}")
print("  " + "-" * 105)
top15 = df[df["top15_flag"] == True].sort_values("composite_score_B", ascending=False)
for i, (_, row) in enumerate(top15.iterrows()):
    print(f"  {i+1:>3d}  {row['cell_id']:>10s}  {row['district']:<25s}  "
          f"{row['composite_score_B']:>7.3f}  {row['intervention_type']:<17s}  "
          f"{row['s1_sealed']:>7.2f}  {row['s2_lst_anomaly']:>7.2f}  "
          f"{row['s3_inverted_ndvi']:>8.2f}  {row['s4_mismatch']:>6.1f}")

# District distribution in top 15
print("\n  Top-15 by district:")
top15_dist = top15["district"].value_counts()
for d, c in top15_dist.items():
    print(f"    {d}: {c}")

# ── 3. INTERVENTION DISTRIBUTION ─────────────────────────────────────────────
print("\n## 3. Intervention Type Distribution")
interv_counts = df["intervention_type"].value_counts()
for label, count in interv_counts.items():
    pct = count / len(df) * 100
    print(f"  {label:<20s}: {count:>3d} cells ({pct:.1f}%)")

# ── 4. DISTRICT-LEVEL SUMMARY ────────────────────────────────────────────────
print("\n## 4. District-Level Summary")
district_summary = (
    df.groupby("district")
    .agg(
        cells=("cell_id", "count"),
        top15_cells=("top15_flag", "sum"),
        mean_score=("composite_score_B", "mean"),
        mean_sealed=("s1_sealed", "mean"),
        mean_lst=("s2_lst_anomaly", "mean"),
        mean_inv_ndvi=("s3_inverted_ndvi", "mean"),
        mean_mismatch=("s4_mismatch", "mean"),
        total_trees=("total_trees", "sum"),
        mean_am_pct=("am_pct", "mean"),
        mean_em_pct=("em_pct", "mean"),
    )
    .sort_values("mean_score", ascending=False)
)

header = (
    f"  {'District':<25s}  {'Cells':>5s}  {'Top15':>5s}  "
    f"{'MeanB':>6s}  {'S1':>6s}  {'S2':>6s}  {'S3':>6s}  "
    f"{'S4':>6s}  {'Trees':>7s}  {'AM%':>5s}  {'EM%':>5s}"
)
print(header)
print("  " + "-" * len(header))
for district, row in district_summary.iterrows():
    print(
        f"  {district:<25s}  {row['cells']:>5.0f}  {row['top15_cells']:>5.0f}  "
        f"{row['mean_score']:>6.3f}  {row['mean_sealed']:>6.2f}  "
        f"{row['mean_lst']:>6.2f}  {row['mean_inv_ndvi']:>6.2f}  "
        f"{row['mean_mismatch']:>6.1f}  {row['total_trees']:>7.0f}  "
        f"{row['mean_am_pct']:>5.1f}  {row['mean_em_pct']:>5.1f}"
    )

# ── 5. SCENARIO COMPARISON ───────────────────────────────────────────────────
print("\n## 5. Scenario Comparison (top-15 overlap)")
top15_A = set(df.nlargest(15, "composite_score_A")["cell_id"])
top15_B_set = set(df.nlargest(15, "composite_score_B")["cell_id"])
top15_C = set(df.nlargest(15, "composite_score_C")["cell_id"])

print(f"  A (equal weights, 0.25/0.25/0.25/0.25): {len(top15_A)} cells")
print(f"  B (sealed-dominant, 0.55/0.20/0.20/0.05): {len(top15_B_set)} cells")
print(f"  C (heat+canopy, 0.17/0.30/0.30/0.23): {len(top15_C)} cells")
print(f"  A n B: {len(top15_A & top15_B_set)} cells")
print(f"  A n C: {len(top15_A & top15_C)} cells")
print(f"  B n C: {len(top15_B_set & top15_C)} cells")
print(f"  A n B n C: {len(top15_A & top15_B_set & top15_C)} cells")

union_ab = top15_A | top15_B_set
union_ac = top15_A | top15_C
union_bc = top15_B_set | top15_C
j_ab = len(top15_A & top15_B_set) / len(union_ab) if union_ab else 0
j_ac = len(top15_A & top15_C) / len(union_ac) if union_ac else 0
j_bc = len(top15_B_set & top15_C) / len(union_bc) if union_bc else 0
print(f"  Jaccard(A,B): {j_ab:.3f}")
print(f"  Jaccard(A,C): {j_ac:.3f}")
print(f"  Jaccard(B,C): {j_bc:.3f}")

# Cells unique to each scenario
print(f"\n  Unique to A only: {top15_A - top15_B_set - top15_C}")
print(f"  Unique to B only: {top15_B_set - top15_A - top15_C}")
print(f"  Unique to C only: {top15_C - top15_A - top15_B_set}")

# ── 6. MYCORRHIZAL TYPE DISTRIBUTION ────────────────────────────────────────
print("\n## 6. Expected Mycorrhizal Type Distribution")
myco_counts = df["expected_myco_type"].value_counts()
for mt, count in myco_counts.items():
    print(f"  {mt:<10s}: {count:>3d} cells ({count/len(df)*100:.1f}%)")

am_dom_count = (df["s4_mismatch"] == 0.5).sum()
print(f"\n  AM-dominant cells (S4=0.5, info-null): "
      f"{am_dom_count} ({am_dom_count/len(df)*100:.1f}%)")
print(f"  EM-dominant cells (S4=0.0): {(df['s4_mismatch'] == 0.0).sum()} "
      f"({(df['s4_mismatch'] == 0.0).sum()/len(df)*100:.1f}%)")
print(f"  EM-isolated cells (S4=0.8): {(df['s4_mismatch'] == 0.8).sum()} "
      f"({(df['s4_mismatch'] == 0.8).sum()/len(df)*100:.1f}%)")

# ── 7. SUB-SCORE CORRELATIONS ───────────────────────────────────────────────
print("\n## 7. Sub-Score Correlation Matrix")
sub_scores = df[
    ["s1_sealed", "s2_lst_anomaly", "s3_inverted_ndvi", "s4_mismatch",
     "composite_score_B"]
]
corr = sub_scores.corr().round(3)
print(f"  {corr.to_string()}")

# ── 8. KEY FINDINGS ─────────────────────────────────────────────────────────
print("\n## 8. Key Findings")

# Highest sealed cells
print("\n  Highest sealed-surface cells:")
highest_sealed = df.nlargest(3, "s1_sealed")
for _, r in highest_sealed.iterrows():
    print(f"    {r['cell_id']} ({r['district']}): sealed={r['s1_sealed']:.2f}, "
          f"composite_B={r['composite_score_B']:.3f}")

# Highest heat anomaly (if real LST data exists)
has_real_lst = df["mean_lst_celsius"].notna().any()
if has_real_lst:
    print("\n  Highest heat anomaly cells:")
    highest_heat = df.nlargest(3, "s2_lst_anomaly")
    for _, r in highest_heat.iterrows():
        print(f"    {r['cell_id']} ({r['district']}): "
              f"lst_anomaly={r['s2_lst_anomaly']:.2f}, "
              f"composite_B={r['composite_score_B']:.3f}")
else:
    print("\n  (S2/LST values are synthetic — raster data unavailable)")

# Lowest NDVI (highest inverted NDVI)
print("\n  Lowest canopy cells (highest inverted NDVI):")
lowest_ndvi = df.nlargest(3, "s3_inverted_ndvi")
for _, r in lowest_ndvi.iterrows():
    print(f"    {r['cell_id']} ({r['district']}): "
          f"inv_ndvi={r['s3_inverted_ndvi']:.2f}, "
          f"composite_B={r['composite_score_B']:.3f}")

# GBIF data quality
gbif_zero = (df["gbif_records"] == 0).sum()
print(f"\n  Cells with zero GBIF records: {gbif_zero} / {len(df)} "
      f"({gbif_zero/len(df)*100:.1f}%)")
print(f"  Mean GBIF records per cell: {df['gbif_records'].mean():.1f}")
print(f"  Max GBIF records in a cell: {df['gbif_records'].max()}")

# Trees
print(f"\n  Total trees in grid: {df['total_trees'].sum():,}")
print(f"  Mean trees per cell: {df['total_trees'].mean():.0f}")
print(f"  Cells with zero trees: {(df['total_trees'] == 0).sum()}")
print(f"  Mean AM%: {df['am_pct'].mean():.1f}%")
print(f"  Mean EM%: {df['em_pct'].mean():.1f}%")
print(f"  Species richness range: {df['species_richness'].min()}-"
      f"{df['species_richness'].max()}")

# ── 9. S4 DETAILED BREAKDOWN ─────────────────────────────────────────────────
print("\n## 9. S4 Mismatch Score Breakdown by Myco Type")
s4_by_myco = (
    df.groupby("expected_myco_type")["s4_mismatch"]
    .agg(["mean", "count"])
    .round(3)
)
print(f"  {s4_by_myco.to_string()}")

# ── 10. INTERVENTION PROFILES FOR TOP 15 ─────────────────────────────────────
print("\n## 10. Intervention Profiles for Top-15 Cells")
for _, row in top15.iterrows():
    profile = row["intervention_profile"]
    # Parse JSON string if needed
    if isinstance(profile, str):
        try:
            profile = json.loads(profile)
        except json.JSONDecodeError:
            profile = {}
    parts = [f"{k}={v:.0f}%" for k, v in profile.items()]
    print(f"  {row['cell_id']:>10s} ({row['district']:<25s}): "
          f"{', '.join(parts)}")

print("\n" + "=" * 70)
print("Analysis complete.")
print("=" * 70)
