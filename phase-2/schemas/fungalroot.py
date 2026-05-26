"""
Pandera schema for FungalRoot v2.0 (Soudzilovskaia et al. 2022).

Source: Zenodo mirror / New Phytologist supplementary data (doi:10.1111/nph.18207).
Two-column lookup table: species_name → myco_type.
Observed: 13,756 rows (not ~14,870 as asserted in data sheet — to verify).

DATA SHEET vs OBSERVED DISAGREEMENTS:
  - Row count: data sheet asserts ~14,870; observed 13,756. Minor disagreement —
    likely version difference or data sheet rounding.
  - myco_type values: data sheet describes short codes (AM, EM, ErM, NM, etc.);
    observed descriptive labels ("EcM, AM undetermined", "non-mycorrhizal", etc.).
    Schema uses OBSERVED values. The pipeline must map these to simplified codes
    for the FungalRoot join (notebook 03-scoring.ipynb).

MYCO_TYPE MAPPING (for downstream pipeline):
  AM → AM
  EcM, AM undetermined → AM (likely, undocumented association)
  EcM, no AM colonization → EM
  EcM,AM → AM+EM (facultative)
  non-mycorrhizal → NM
  non-ectomycorrhizal (AM undetermined) → AM (likely)
  ErM → ErM
  ErM,EcM → ErM+EM
  OM → OM
  AM-like (non-vascular plants) → NM (non-vascular — exclude from tree join)
  Other → unknown (exclude or flag)
"""

import pandera as pa
from pandera.typing import Series

OBSERVED_MYCO_TYPES = [
    "AM",
    "EcM, AM undetermined",
    "EcM, no AM colonization",
    "EcM,AM",
    "non-mycorrhizal",
    "non-ectomycorrhizal (AM undetermined)",
    "ErM",
    "ErM,EcM",
    "OM",
    "AM-like (non-vascular plants)",
    "Other",
]


class FungalRootSchema(pa.DataFrameModel):
    """One row = one plant species → mycorrhizal type assignment."""

    species_name: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Scientific name (genus + epithet); 13,756 unique species observed",
    )

    myco_type: Series[str] = pa.Field(
        nullable=False,
        isin=OBSERVED_MYCO_TYPES,
        description=(
            "Mycorrhizal type assignment from published literature. "
            "Descriptive labels as published. Distribution: AM=70.0%, "
            "non-mycorrhizal=16.6%, EcM-variants=8.7%, Other=2.2%, "
            "ErM=1.0%, OM=1.1%, ErM,EcM=0.04%, AM-like=0.1%."
        ),
    )

    class Config:
        coerce = True
        strict = False
