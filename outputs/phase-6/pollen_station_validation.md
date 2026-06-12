# XAC Pollen Station Spot-Check

**Scope:** n=1 in-city station; directional check only, not a calibration

**Calibration status:** NOT FEASIBLE with current data. Annual pollen totals (grains x day / m3 per year) are not accessible via the public XAC API, which only exposes 7-day forecasts on a 0-4 ordinal scale. Contact aerobiologia@uab.cat for the historical Platanus series.

---

## Barcelona (in-grid)

| Field | Value |
|---|---|
| Cell | `C023_022` |
| District | EIXAMPLE |
| Plane trees | 184 |
| Maturity | 0.98 |
| source_raw | 180.0 |
| source_std | 0.389 |
| **Percentile (all cells)** | **86th -- top 25%** |
| Percentile (cells with planes) | 83th |
| Live API (XAC) | Platanus level = 1/4 (0=null, 4=max) |

## Bellaterra (in-grid)

| Field | Value |
|---|---|
| Cell | `C025_041` |
| District | NOU BARRIS |
| Plane trees | 0 |
| Maturity | 1.00 |
| source_raw | 0.0 |
| source_std | 0.000 |
| **Percentile (all cells)** | **16th -- bottom 25%** |
| Percentile (cells with planes) | 0th |
| Live API (XAC) | Platanus level = 0/4 (0=null, 4=max) |

---

## Honest limitations

- **n=1 in-city station.** Spatial calibration across cells requires >= ~10 stations.
- The percentile check answers only: *is the station area notable per our proxy?*
  It cannot confirm whether the proxy rank order is correct city-wide.
- The XAC public API exposes 7-day forecast levels (0-4 ordinal) only.
  Annual pollen season integrals (grains x day / m3) are not accessible.
- **To close model-card limitation #1** (not validated against measured pollen),
  request the historical Platanus series from aerobiologia@uab.cat and populate
  an `annual_pollen_index` column in `data/pollen_stations.csv`, then re-run.

## What full calibration would require

1. Annual pollen season integral for Barcelona station (5+ years) from XAC archives.
2. Tree-inventory snapshots for the same years to match inter-annual proxy changes.
3. At least 2-3 additional in-city stations for any spatial regression across cells.