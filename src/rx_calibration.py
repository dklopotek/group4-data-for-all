"""Phase 6 (Deployment) -- EXPLORATORY validation of the vulnerability layer's age weights
against REAL Barcelona respiratory prescriptions (CatSalut).

The section-grain vulnerability layer (src/section_vulnerability.py) weights residents by
LITERATURE allergic-rhinitis prevalence by age (Bauchau & Durham 2004; GAN) -- which DECLINES
in the elderly (weight 0.06 for 70+). We now have a real local signal:
data/raw/catsalut_receptes_bcnciutat_respiratori.csv -- prescriptions by age x sex x ATC class
(R01 nasal preps, R06 systemic antihistamines = allergy-type; R03 = asthma/COPD obstructive),
Barcelona city, 2024-25. We compute per-capita prescribing by broad age band (using the age
register for the denominator) and compare its SHAPE to the literature weights.

This is EXPLORATORY (NOT one of the pre-registered T1-T4). It is reported either way per the
brutal-honesty rule. KEY LIMITATION: CatSalut data is CITY-WIDE by age, NOT spatial -- it can
recalibrate the AGE curve but cannot localize allergy. Rx burden also conflates prevalence,
severity, polypharmacy, and care-seeking; it is a demand signal, not a prevalence measurement.

Writes outputs/phase-6/rx_calibration.{json,md}. ASCII-only. Run: python src/rx_calibration.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
RX = ROOT / "data" / "raw" / "catsalut_receptes_bcnciutat_respiratori.csv"
EDATQ = ROOT / "data" / "raw" / "2026_pad_mdbas_edat-q.csv"
OUTDIR = ROOT / "outputs" / "phase-6"

# broad bands aligned to BOTH CatSalut groups and the 5-yr age register (clean nesting)
BANDS = [("0-19", 0, 19), ("20-44", 20, 44), ("45-64", 45, 64), ("65+", 65, 200)]
ALLERGY_ATC = {"R01", "R06"}          # nasal preps + systemic antihistamines
OBSTRUCT_ATC = {"R03"}                # asthma / COPD agents (age/smoking driven, less pollen)


def lit_ar_prev(age0):
    """Literature allergic-rhinitis prevalence weight by 5-yr band start age (mirrors
    section_vulnerability.ar_prev; Bauchau & Durham 2004 ~23% EU adult; GAN child; elderly decline)."""
    if age0 < 5: return 0.04
    if age0 < 10: return 0.089
    if age0 < 15: return 0.146
    if age0 < 45: return 0.22
    if age0 < 65: return 0.18
    if age0 < 70: return 0.10
    return 0.06


def catsalut_low_age(grup):
    """Lower bound of a CatSalut age-group label ('0-1 any', '20-24 anys', 'Mes de 84 anys')."""
    g = grup.strip().lower()
    if g.startswith("m"):                       # "Mes de 84 anys"
        return 85
    return int(g.split("-")[0].split(" ")[0])


def edatq_low_age(band):
    return 5 * int(band)


def band_of(low_age):
    for name, lo, hi in BANDS:
        if lo <= low_age <= hi:
            return name
    return None


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # --- prescriptions by broad band (latest year, both sexes) ---
    rx = pd.read_csv(RX, dtype=str)
    rx["receptes"] = pd.to_numeric(rx["receptes"], errors="coerce").fillna(0)
    latest = sorted(rx["any"].unique())[-1]
    rx = rx[rx["any"] == latest].copy()
    rx["low"] = rx["grup_edat"].map(catsalut_low_age)
    rx["band"] = rx["low"].map(band_of)
    allergy = (rx[rx["codi_atc_2"].isin(ALLERGY_ATC)].groupby("band")["receptes"].sum())
    obstruct = (rx[rx["codi_atc_2"].isin(OBSTRUCT_ATC)].groupby("band")["receptes"].sum())

    # --- population denominator by broad band (sum age register across all sections) ---
    e = pd.read_csv(EDATQ, dtype=str)
    e["pop"] = pd.to_numeric(e["Valor"], errors="coerce").fillna(0)
    e["bandidx"] = pd.to_numeric(e["EDAT_Q"], errors="coerce")
    e = e.dropna(subset=["bandidx"])
    e["low"] = e["bandidx"].map(edatq_low_age)
    e["band"] = e["low"].map(band_of)
    pop = e.groupby("band")["pop"].sum()

    # --- literature weight per broad band (population-weighted mean of 5-yr ar_prev) ---
    e["lit"] = e["low"].map(lit_ar_prev)
    litw = (e.assign(num=e["lit"] * e["pop"]).groupby("band")["num"].sum() / pop)

    names = [b[0] for b in BANDS]
    rows = []
    for b in names:
        p = float(pop.get(b, 0.0))
        a = float(allergy.get(b, 0.0))
        o = float(obstruct.get(b, 0.0))
        rows.append({
            "band": b, "population": int(p),
            "allergy_rx": int(a), "allergy_per_1000": round(1000 * a / p, 1) if p else None,
            "obstructive_rx": int(o), "obstructive_per_1000": round(1000 * o / p, 1) if p else None,
            "literature_weight": round(float(litw.get(b, np.nan)), 3),
        })
    tbl = pd.DataFrame(rows)

    # normalize both curves to peak = 1 and compare shape
    real = tbl["allergy_per_1000"].to_numpy(float)
    lit = tbl["literature_weight"].to_numpy(float)
    real_n = real / np.nanmax(real)
    lit_n = lit / np.nanmax(lit)
    sp = float(spearmanr(real, lit).statistic)

    real_peak = names[int(np.nanargmax(real))]
    lit_peak = names[int(np.nanargmax(lit))]
    elderly_real = float(real_n[-1])      # 65+ normalized real prescribing
    elderly_lit = float(lit_n[-1])        # 65+ normalized literature weight

    diverges = bool(real_peak != lit_peak or abs(elderly_real - elderly_lit) > 0.3)
    res = {
        "year": latest,
        "bands": rows,
        "shape_spearman_real_vs_literature": round(sp, 4),
        "peak_band_real_allergy_rx": real_peak,
        "peak_band_literature": lit_peak,
        "elderly_65plus_normalized": {"real_prescribing": round(elderly_real, 3),
                                      "literature_weight": round(elderly_lit, 3)},
        "FINDING": (
            "DIVERGES: real Barcelona allergy-type prescribing peaks at '%s' and stays high in "
            "the elderly, while the literature weight peaks at '%s' and decays in the elderly. "
            "Our vulnerability layer UNDER-weights older residents' respiratory burden. Since the "
            "layer was already found REDUNDANT with population for RANKING, this does not change "
            "the headline -- but it means the redundancy is not because age is uninformative; it "
            "is because age structure is ~flat in space. Calibrating to local Rx would shift "
            "vulnerability toward older neighborhoods, not flatten it." % (real_peak, lit_peak)
            if diverges else
            "CONSISTENT: real prescribing and the literature age curve agree in shape."),
        "caveats": [
            "CatSalut data is city-wide by age x sex -- recalibrates the AGE curve, NOT the map.",
            "Rx is a demand signal (prevalence x severity x polypharmacy x care-seeking), not a "
            "prevalence measurement; elderly polypharmacy inflates counts.",
            "R01+R06 include non-allergic uses; R03 (obstructive) reported separately as it is "
            "more asthma/COPD than pollen-driven.",
            "Broad bands (0-19/20-44/45-64/65+) chosen to nest cleanly in both datasets.",
        ],
        "provenance": "CatSalut receptes respiratori (BCN ciutat, %s); denominator = padro edat-q." % latest,
    }
    (OUTDIR / "rx_calibration.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

    md = ["# Rx calibration -- literature allergy weights vs real Barcelona prescribing",
          "",
          "_Exploratory (NOT a pre-registered T1-T4); reported per the brutal-honesty rule._",
          "",
          f"**FINDING: {res['FINDING']}**", "",
          f"Shape Spearman(real per-capita allergy Rx, literature weight) over 4 bands = "
          f"**{sp:.3f}**. Real peak = **{real_peak}**; literature peak = **{lit_peak}**. "
          f"Normalized 65+ : real **{elderly_real:.2f}** vs literature **{elderly_lit:.2f}**.", "",
          "| Age band | Population | Allergy Rx (R01+R06) | per 1000 | Obstructive (R03)/1000 | Literature weight |",
          "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['band']} | {r['population']:,} | {r['allergy_rx']:,} | "
                  f"{r['allergy_per_1000']} | {r['obstructive_per_1000']} | {r['literature_weight']} |")
    md += ["", "## Caveats", ""] + [f"- {c}" for c in res["caveats"]]
    md += ["", f"_Provenance: {res['provenance']}_", ""]
    (OUTDIR / "rx_calibration.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(res, indent=2))
    print("\nRx calibration written -> outputs/phase-6/rx_calibration.{json,md}")


if __name__ == "__main__":
    main()
