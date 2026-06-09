"""Sex comparison of allergy/respiratory burden, Barcelona city-wide.

Empirical: CatSalut prescriptions by sex (2025) per capita, using city
population by sex (Padro 2026). Antihistamines (R06) are the clearest allergy
signal. City-wide only -- no sub-city sex-risk data exists, and the sex ratio is
near-constant across neighbourhoods, so this does NOT add a mappable layer (same
redundancy lesson as age-weighting). It answers the epidemiological question.

ASCII-only. Run:  python src/sex_atrisk.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRESC = ROOT / "data" / "raw" / "catsalut_receptes_bcnciutat_respiratori.csv"
SEXPOP = ROOT / "data" / "raw" / "2026_pad_mdbas_sexe.csv"
OUT = ROOT / "outputs" / "phase-6" / "sex_atrisk.md"

# Barcelona is women-majority (~51.9%); larger SEXE group = women (Dona).
ps = pd.read_csv(SEXPOP, dtype=str)
ps["v"] = pd.to_numeric(ps["Valor"], errors="coerce").fillna(0)
bysex = ps.groupby("SEXE")["v"].sum().sort_values(ascending=False)
women_pop, men_pop = float(bysex.iloc[0]), float(bysex.iloc[1])

p = pd.read_csv(PRESC, dtype=str)
p["rec"] = pd.to_numeric(p["receptes"], errors="coerce").fillna(0)
p = p[p["any"] == "2025"]
rows = []
labels = {"R06": "Antihistamines (systemic) - clearest allergy signal",
          "R01": "Nasal preparations", "R03": "Obstructive-airway agents (asthma/COPD)"}
for atc, lab in labels.items():
    s = p[p["codi_atc_2"] == atc].groupby("sexe")["rec"].sum()
    w, m = float(s.get("Dona", 0)), float(s.get("Home", 0))
    wr, mr = 1000 * w / women_pop, 1000 * m / men_pop
    rows.append((atc, lab, w, m, wr, mr, wr / mr if mr else float("nan")))

md = [f"# Allergy/respiratory burden by sex - Barcelona, 2025 (city-wide)\n",
      f"Population: women {women_pop:,.0f}, men {men_pop:,.0f} (Padro 2026; "
      f"Barcelona is women-majority so the larger SEXE group is women).\n",
      "| Drug class | women rx | men rx | women /1000 | men /1000 | ratio W:M |",
      "|---|---|---|---|---|---|"]
for atc, lab, w, m, wr, mr, ratio in rows:
    md.append(f"| {atc} {lab} | {w:,.0f} | {m:,.0f} | {wr:.1f} | {mr:.1f} | {ratio:.2f} |")
md += [
    "\n## Answer",
    "- **Yes, a sex is more affected.** For antihistamines (R06, the clearest allergy "
    f"signal) women receive **{rows[0][6]:.2f}x** the per-capita prescriptions of men "
    f"({rows[0][4]:.0f} vs {rows[0][5]:.0f} per 1000).",
    "- The gap is largest for antihistamines and smaller for nasal/airway drugs.",
    "\n## Honest caveats",
    "- This is **medication use, not pure prevalence**. Women seek care and are prescribed "
    "more across most drug classes (a known healthcare-utilization sex bias), so part of the "
    "gap is utilization, not biology.",
    "- **Literature nuance (age-dependent switch):** in CHILDHOOD allergic rhinitis/asthma is "
    "more common in BOYS; after puberty it switches and ADULT AR/asthma is higher in WOMEN. So "
    "'who is most at risk' depends on age.",
    "- **City-wide only.** No sub-city sex-allergy data exists, and the sex ratio is near-"
    "constant across neighbourhoods -- so a sex weighting would be redundant with population "
    "for the spatial priority (same finding as age-weighting). This answers the epidemiological "
    "question; it does not add a mappable layer.",
]
OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
