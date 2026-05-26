# Success Criteria

## Business Success Criteria

| Business Success Criterion | Numerical Threshold | Deadline | Owner |
|---|---|---|---|
| Priority map used in at least one Ajuntament green-infrastructure budget recommendation | ≥ 1 planning cycle | FY2027 | Ajuntament Espais Verds i Biodiversitat (seminar: teacher evaluates pipeline, not adoption) |
| Every recommended intervention type maps to a documented Ajuntament budget line | 4 of 4 intervention types mapped | Session 4 submission | Project team |
| Output is comprehensible to a non-mycologist planning analyst | User reads product card + map and correctly answers "what should we do in zone X" without consulting the team | Session 4 submission | Project team |
| Shortlist of priority zones is actionable within existing institutional process | ≤ 15 zones recommended | Session 4 submission | Project team |

## Data-Product Success Criteria

| Data-Product Success Criterion | Numerical Threshold | Verification Method |
|---|---|---|
| Spatial coverage | ≥ 95% of grid cells within Barcelona municipal boundary have non-null barrier_index | `notebooks/00-data-validation.ipynb` spatial coverage check |
| Row count accountability | Every transformation logs rows-in / rows-out; rejected rows have reason_code | Manual audit of notebook markdown cells |
| Bounds validity | NDVI ∈ [−1, 1]; LST ∈ [15, 55] °C; sealed surface ∈ [0, 100]%; coordinates within Barcelona bbox | `notebooks/00-data-validation.ipynb` bounds assertions |
| Composite score range | barrier_index ∈ [0, 1] for all zones | Assertion in notebook 03 |
| Reproducibility | Pipeline produces bit-identical output from a clean clone with fresh data downloads | Single clean-clone re-run (seminar: documented design is sufficient; full re-run ideal) |
| Intervention-type cardinality | Every zone with barrier_index > 0 has exactly one intervention_type value ∈ {de-paving, planting, species-selection, combined} | Assertion in notebook 03 |
| Peri-urban reference patch | Exactly 1 reference patch exists, excluded from priority ranking, documented as methodological anchor | Manual verification in output GeoJSON |
| Product card completeness | Product card has ≥ 2 out-of-scope uses, ≥ 3 known limitations, intended user named | Manual audit of `phase-1/product-card-draft.md` |
