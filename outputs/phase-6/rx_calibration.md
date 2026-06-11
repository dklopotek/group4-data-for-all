# Rx calibration -- literature allergy weights vs real Barcelona prescribing

_Exploratory (NOT a pre-registered T1-T4); reported per the brutal-honesty rule._

**FINDING: DIVERGES: real Barcelona allergy-type prescribing peaks at '65+' and stays high in the elderly, while the literature weight peaks at '20-44' and decays in the elderly. Our vulnerability layer UNDER-weights older residents' respiratory burden. Since the layer was already found REDUNDANT with population for RANKING, this does not change the headline -- but it means the redundancy is not because age is uninformative; it is because age structure is ~flat in space. Calibrating to local Rx would shift vulnerability toward older neighborhoods, not flatten it.**

Shape Spearman(real per-capita allergy Rx, literature weight) over 4 bands = **-0.400**. Real peak = **65+**; literature peak = **20-44**. Normalized 65+ : real **1.00** vs literature **0.32**.

| Age band | Population | Allergy Rx (R01+R06) | per 1000 | Obstructive (R03)/1000 | Literature weight |
|---|---|---|---|---|---|
| 0-19 | 264,735 | 58,876 | 222.4 | 231.2 | 0.133 |
| 20-44 | 637,535 | 185,665 | 291.2 | 143.6 | 0.22 |
| 45-64 | 463,513 | 240,333 | 518.5 | 469.0 | 0.18 |
| 65+ | 362,090 | 270,781 | 747.8 | 1358.5 | 0.07 |

## Caveats

- CatSalut data is city-wide by age x sex -- recalibrates the AGE curve, NOT the map.
- Rx is a demand signal (prevalence x severity x polypharmacy x care-seeking), not a prevalence measurement; elderly polypharmacy inflates counts.
- R01+R06 include non-allergic uses; R03 (obstructive) reported separately as it is more asthma/COPD than pollen-driven.
- Broad bands (0-19/20-44/45-64/65+) chosen to nest cleanly in both datasets.

_Provenance: CatSalut receptes respiratori (BCN ciutat, 2025); denominator = padro edat-q._
