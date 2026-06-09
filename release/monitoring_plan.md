# Monitoring & Maintenance Plan

CRISP-DM Phase 6 "Plan Monitoring and Maintenance". The product is a batch data pipeline, not a live
service, so monitoring = source-drift watch + dependency rot + a release trigger, not uptime.

## Inputs monitored (check cadence)
| Input | Drift risk | Cadence | Action on change |
|---|---|---|---|
| Street-tree inventory (`arbrat-viari.csv`) | New plantings/removals shift plane counts & maturity | Annual (matches city inventory updates) | Re-run `section_priority.py` + `street_actions.py`; bump MINOR |
| Population register (Padro) | Demographic shift changes exposure | Annual (new Padro) | Re-run; bump MINOR |
| Census-section polygons | Boundary revision changes the join | On municipal re-districting | Re-verify the section-key join (1,068 expected); bump MAJOR if grain changes |
| *Pla Director* removal target | Policy revision changes `TARGET_REMOVE` | On policy update | Edit `street_actions.py` constant; re-run allocation only |

## Dependencies monitored
- Rebuild the pinned env from `release/requirements-lock.txt` annually; if geopandas/GDAL breaks the
  build, re-pin and re-verify the manifest SHA-256s.
- Link check on the Open Data BCN source URLs (reference rot); update `data/raw/SOURCES.md` if moved.

## Triggers for a NEW release (semantic version)
- **PATCH:** doc fix, no output change.
- **MINOR:** refreshed input (inventory/Padro) re-run, same method.
- **MAJOR:** method change (new layer, new grain, new aggregation), or a measured-pollen series enabling
  source validation — which would re-open Phase 1 (new CRISP-DM cycle).

## Named maintainer
**Group 4 (MaAI01 25-26), point of contact: Rafik El Khoury** for the duration of the seminar.
After the seminar: **unmaintained — fork freely** under the stated licences. (Stated explicitly; no
ambiguous "TBD".)

## Ownership transfer
On maintainer departure: the repo + this release bundle + the data contract
(`phase-6/allergen-data-contract.yaml`) are self-describing and reproducible from
`release/how_to_rerun.md`; any successor can rebuild without contacting the original authors.

## Deprecation
When a vMAJOR supersedes this product, tag the old release, keep its DOI/landing live as a tombstone,
and link forward. Do not delete superseded outputs.

## Re-run cadence
Annual by default (aligns with budget cycle), or on any trigger above.
