"""Improvement #4 -- per-tree COST model for plane removal + replacement (euros).

Anchored to the CoolSpend cost model (a sibling Barcelona project; OneDrive/Python
Resources/.../coolspend/cost_model.py), itself sourced to BCN Verd Urba (tree stock),
structural-soil installation, Diputacio BCN labour grant, and BCN IMPJ 2023 maintenance.
Those figures are for PLANTING; we add an illustrative felling/removal line for the
remove-then-replace intervention this project sequences.

ALL FIGURES are "illustrative European/Barcelona mid-range, verify locally" -- same honesty
posture as CoolSpend's confidence tags (VERIFIED / DECLARED / PENDING). They scale a budget;
they are NOT a procurement quote.

Run:  python src/cost_model_bcn.py   (prints the cost table + a few budget conversions)
"""
from __future__ import annotations

# --- CapEx, replacement tree (EUR/tree) -- from CoolSpend DEFAULT_COST_TABLE (sum = 2200) ---
CAPEX_REPLACEMENT_EUR = 2200.0       # fully-loaded new large-caliper pit
#   tree_stock 600 (DECLARED, BCN Verd Urba 20-25cm) + structural_soil 600 (DECLARED)
#   + pit/excavation + irrigation (DECLARED) + planting_labour 300 (VERIFIED, Diputacio BCN)

# --- Felling/removal of the existing mature plane (EUR/tree) -- ILLUSTRATIVE, not in CoolSpend ---
REMOVAL_FELLING_EUR = 450.0          # DECLARED illustrative: mature street-tree fell + stump grind

# --- OpEx on the replacement (EUR/tree/yr) -- from CoolSpend (VERIFIED, BCN IMPJ 2023) ---
OPEX_EUR_YEAR = 60.0
OPEX_HORIZON_YEARS = 40
DISCOUNT_RATE = 0.035                # EU/UK Green Book social convention (locale-editable)

# Headline planning unit cost = remove one plane + plant one replacement (CapEx only).
INTERVENTION_CAPEX_EUR = CAPEX_REPLACEMENT_EUR + REMOVAL_FELLING_EUR    # 2650

PROVENANCE = ("CoolSpend cost_model (BCN Verd Urba / Diputacio BCN / IMPJ 2023); "
              "removal line illustrative. Figures are mid-range, verify locally.")


def opex_pv_per_tree() -> float:
    """Present value of OpEx over the horizon at the discount rate (EUR/tree)."""
    r = DISCOUNT_RATE
    return sum(OPEX_EUR_YEAR / (1 + r) ** y for y in range(OPEX_HORIZON_YEARS))


def lifecycle_cost_per_tree(include_opex: bool = True) -> float:
    c = INTERVENTION_CAPEX_EUR
    return c + opex_pv_per_tree() if include_opex else c


def trees_for_budget(eur: float, include_opex: bool = False) -> int:
    """How many remove+replace interventions a euro budget buys (CapEx basis by default)."""
    unit = lifecycle_cost_per_tree(include_opex)
    return int(eur // unit) if unit > 0 else 0


def cost_for_trees(n: int, include_opex: bool = False) -> float:
    return n * lifecycle_cost_per_tree(include_opex)


def as_dict() -> dict:
    return {
        "capex_replacement_eur": CAPEX_REPLACEMENT_EUR,
        "removal_felling_eur": REMOVAL_FELLING_EUR,
        "intervention_capex_eur": INTERVENTION_CAPEX_EUR,
        "opex_eur_year": OPEX_EUR_YEAR,
        "opex_horizon_years": OPEX_HORIZON_YEARS,
        "discount_rate": DISCOUNT_RATE,
        "opex_pv_per_tree_eur": round(opex_pv_per_tree(), 2),
        "lifecycle_cost_per_tree_eur": round(lifecycle_cost_per_tree(True), 2),
        "provenance": PROVENANCE,
        "caveat": "Illustrative mid-range; scales a budget, not a procurement quote. Locale-editable.",
    }


if __name__ == "__main__":
    import json
    d = as_dict()
    print(json.dumps(d, indent=2))
    print(f"\n  intervention CapEx (remove+replace): EUR {INTERVENTION_CAPEX_EUR:,.0f}/tree")
    print(f"  lifecycle (CapEx + OpEx PV {OPEX_HORIZON_YEARS}yr @ {DISCOUNT_RATE:.1%}): "
          f"EUR {lifecycle_cost_per_tree(True):,.0f}/tree")
    for b in (100_000, 500_000, 1_000_000):
        print(f"  EUR {b:>9,} -> {trees_for_budget(b):>4} trees (CapEx) / "
              f"{trees_for_budget(b, True):>4} trees (lifecycle)")
