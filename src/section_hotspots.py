"""Cycle-B Phase-4 Model #3 -- HOTSPOT LAYER (inferential spatial statistics).

Getis-Ord Gi* (Getis & Ord 1992; Ord & Getis 1995) and Local Moran's I / LISA
(Anselin 1995) on the section priority surface, with a queen-contiguity spatial weights
matrix and 999-permutation pseudo-p-values. Hand-rolled (numpy) -- no PySAL dependency.

Turns an arbitrary top-N into statistically defensible hot/cold clusters and flags spatial
outliers (e.g. a high-source parkland section in a low-neighbourhood = High-Low). Extends the
global Moran's I already used in Phase 5. Deterministic (seed 42), ASCII-only.
Run:  python src/section_hotspots.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import geopandas as gpd

SEED = 42
NPERM = 999
ROOT = Path(__file__).resolve().parents[1]
SECP = ROOT / "outputs" / "phase-6" / "section_priority.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
DESIGN = ROOT / "phase-6" / "modeling-ml-design.md"
MONTJUIC = "03024"


def neighbors(gdf):
    idx = gdf.sindex
    geoms = gdf.geometry.values
    nb = []
    for i, g in enumerate(geoms):
        js = [int(j) for j in idx.query(g, predicate="intersects") if int(j) != i]
        nb.append(js)
    return nb


def gi_star(x, nb):
    """Getis-Ord Gi* z-scores (binary weights including self)."""
    n = len(x); xbar = x.mean(); S = np.sqrt((x**2).mean() - xbar**2)
    z = np.empty(n)
    for i in range(n):
        members = nb[i] + [i]                       # include self -> Gi*
        Wi = len(members)
        lag = x[members].sum()
        denom = S * np.sqrt((n * Wi - Wi**2) / (n - 1))
        z[i] = (lag - xbar * Wi) / denom if denom > 0 else 0.0
    return z


def local_moran(x, nb, rng):
    """Local Moran's I_i with conditional-permutation pseudo-p and quadrant labels."""
    n = len(x); z = (x - x.mean()) / x.std()
    Ii = np.empty(n); lag = np.empty(n); p = np.empty(n)
    for i in range(n):
        ni = nb[i]
        if not ni:
            Ii[i] = 0; lag[i] = 0; p[i] = 1.0; continue
        wlag = z[ni].mean()                          # row-standardized lag
        lag[i] = wlag
        Ii[i] = z[i] * wlag
        others = np.delete(z, i)
        k = len(ni)
        perm = rng.choice(others, size=(NPERM, k), replace=True).mean(axis=1)
        perm_I = z[i] * perm
        p[i] = (np.sum(np.abs(perm_I) >= abs(Ii[i])) + 1) / (NPERM + 1)
    quad = np.where(z >= 0, np.where(lag >= 0, "HH", "HL"),
                    np.where(lag >= 0, "LH", "LL"))
    return Ii, lag, p, quad, z


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    g = gpd.read_parquet(SECP).reset_index(drop=True)
    x = g["priority"].to_numpy(float)
    nb = neighbors(g)
    rng = np.random.default_rng(SEED)

    giz = gi_star(x, nb)
    # two-sided normal p for Gi*
    from math import erf
    gip = np.array([2 * (1 - 0.5 * (1 + erf(abs(zz) / np.sqrt(2)))) for zz in giz])
    hot = (giz > 0) & (gip < 0.05)
    cold = (giz < 0) & (gip < 0.05)

    Ii, lag, lmp, quad, z = local_moran(x, nb, rng)
    sig = lmp < 0.05

    g2 = g.copy()
    g2["gi_z"] = giz; g2["gi_p"] = gip
    g2["hotspot"] = np.where(hot, "hot", np.where(cold, "cold", "ns"))
    g2["lisa_quadrant"] = np.where(sig, quad, "ns")
    g2["lisa_p"] = lmp
    cols = ["key", "district_lbl", "priority", "gi_z", "gi_p", "hotspot",
            "lisa_quadrant", "lisa_p"]
    g2[cols].sort_values("gi_z", ascending=False).to_csv(
        OUTDIR / "section_hotspots.csv", index=False)

    mj = g2[g2["key"] == MONTJUIC]
    mj_class = (f"Gi* {float(mj['gi_z'].iloc[0]):.2f} ({mj['hotspot'].iloc[0]}), "
                f"LISA {mj['lisa_quadrant'].iloc[0]}" if len(mj) else "not found")

    res = {
        "n": int(len(g)), "n_permutations": NPERM,
        "gi_star": {"hot_p<0.05": int(hot.sum()), "cold_p<0.05": int(cold.sum())},
        "lisa_quadrants_sig": {q: int(((quad == q) & sig).sum())
                               for q in ("HH", "LL", "HL", "LH")},
        "montjuic_03024": mj_class,
        "top_hot_sections": g2[hot].sort_values("gi_z", ascending=False)
            .head(8)[["key", "district_lbl", "priority", "gi_z"]].to_dict("records"),
    }
    res["VERDICT"] = (
        f"{res['gi_star']['hot_p<0.05']} significant priority hot-spots and "
        f"{res['lisa_quadrants_sig']['HL']} High-Low spatial outliers identified; "
        f"Montjuic 03024 = {mj_class} (the parkland-outlier check).")

    (OUTDIR / "section_hotspots.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    _write_md(res); _append_design(res)
    print(json.dumps(res, indent=2))


def _write_md(res):
    hot = "\n".join(f"| {r['key']} | {r['district_lbl']} | {round(r['priority'],4)} | {round(r['gi_z'],2)} |"
                    for r in res["top_hot_sections"])
    md = f"""# Hotspot Layer (Cycle-B Phase-4 Model #3)

Getis-Ord Gi* + Local Moran's I (LISA) on section priority; queen contiguity, {res['n_permutations']}
permutations. Inferential stats on observed values -> non-tautological.

**VERDICT: {res['VERDICT']}**

- **Gi\\*:** {res['gi_star']['hot_p<0.05']} hot-spots, {res['gi_star']['cold_p<0.05']} cold-spots (p<0.05).
- **LISA significant quadrants:** {json.dumps(res['lisa_quadrants_sig'])}
  (HH = priority cluster; HL = high section in a low neighbourhood = the MAUP/park outlier signature).
- **Montjuic 03024:** {res['montjuic_03024']}.

## Top hot-spot sections (Gi* z)
| key | district | priority | Gi* z |
|---|---|---|---|
{hot}

Per-section classification: `outputs/phase-6/section_hotspots.csv`.
"""
    (OUTDIR / "section_hotspots.md").write_text(md, encoding="utf-8")


def _append_design(res):
    if not DESIGN.exists():
        return
    txt = DESIGN.read_text(encoding="utf-8")
    anchor = "(hotspot results appended below.)"
    block = (anchor + "\n\n### Model #3 -- hotspots\n\n"
             f"**{res['VERDICT']}** Gi*: {res['gi_star']['hot_p<0.05']} hot / "
             f"{res['gi_star']['cold_p<0.05']} cold (p<0.05). LISA sig quadrants "
             f"{json.dumps(res['lisa_quadrants_sig'])}. Full: `outputs/phase-6/section_hotspots.md`.")
    if anchor in txt:
        DESIGN.write_text(txt.replace(anchor, block), encoding="utf-8")


if __name__ == "__main__":
    main()
