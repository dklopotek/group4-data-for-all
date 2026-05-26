"""
Pandera schema for parsed GBIF fungal occurrence records (Barcelona subset).

Source: GBIF Occurrence API → JSON → parsed to flat DataFrame.
Darwin Core standard fields, subset to the columns used in our pipeline.
Barcelona municipal subset: 1,023 records, 2015–2024, 98.3% HUMAN_OBSERVATION.

This schema describes the PARSED state after the GBIF JSON response is flattened
into a tabular DataFrame in the profiling/preparation notebook. It is NOT a schema
for the raw nested JSON — that is validated at ingestion time via file hash only.
"""

import pandera as pa
from pandera.typing import Series


class GbifFungiSchema(pa.DataFrameModel):
    """One row = one flattened fungal occurrence record, Darwin Core fields."""

    gbifID: Series[int] = pa.Field(
        nullable=False,
        unique=True,
        description="GBIF unique occurrence identifier",
    )

    scientificName: Series[str] = pa.Field(
        nullable=False,
        description="Full scientific name as reported by publisher",
    )

    kingdom: Series[str] = pa.Field(
        nullable=False,
        isin=["Fungi"],
        description="Kingdom; must be Fungi per our API filter",
    )

    decimalLatitude: Series[float] = pa.Field(
        nullable=False,
        ge=41.30,
        le=41.48,
        description="WGS84 latitude; filtered to Barcelona municipality",
    )

    decimalLongitude: Series[float] = pa.Field(
        nullable=False,
        ge=2.05,
        le=2.23,
        description="WGS84 longitude; filtered to Barcelona municipality",
    )

    coordinateUncertaintyInMeters: Series[float] = pa.Field(
        nullable=True,
        ge=0,
        le=100,
        description=(
            "Coordinate uncertainty in metres. Nullable — some records lack "
            "this field. Our pipeline filter: keep if missing OR ≤100m. "
            "Records with uncertainty >100m are excluded upstream of this schema."
        ),
    )

    eventDate: Series[str] = pa.Field(
        nullable=True,
        description="Observation date in ISO 8601 or partial-date format. 2015–2024 range.",
    )

    basisOfRecord: Series[str] = pa.Field(
        nullable=False,
        isin=[
            "HUMAN_OBSERVATION",
            "PRESERVED_SPECIMEN",
            "MATERIAL_SAMPLE",
            "OCCURRENCE",
            "LIVING_SPECIMEN",
            "MACHINE_OBSERVATION",
            "FOSSIL_SPECIMEN",
        ],
        description="Basis of record. 98.3% HUMAN_OBSERVATION in our subset.",
    )

    recordedBy: Series[str] = pa.Field(
        nullable=True,
        description="Observer or collector name; frequently missing",
    )

    taxonRank: Series[str] = pa.Field(
        nullable=True,
        isin=["SPECIES", "GENUS", "FAMILY", "ORDER", "CLASS", "PHYLUM", "KINGDOM", "SUBSPECIES", "VARIETY", "FORM"],
        description="Taxonomic rank of the identification",
    )

    genus: Series[str] = pa.Field(
        nullable=True,
        description="Genus name from taxonomic hierarchy",
    )

    specificEpithet: Series[str] = pa.Field(
        nullable=True,
        description="Specific epithet from taxonomic hierarchy",
    )

    datasetKey: Series[str] = pa.Field(
        nullable=False,
        description="UUID of publishing dataset",
    )

    license: Series[str] = pa.Field(
        nullable=False,
        isin=["CC0_1_0", "CC_BY_4_0", "CC_BY_NC_4_0"],
        description="Per-record license. NC-licensed records may require exclusion from redistribution.",
    )

    occurrenceStatus: Series[str] = pa.Field(
        nullable=False,
        isin=["PRESENT", "ABSENT"],
        description="Occurrence status; nearly always PRESENT for our subset",
    )

    phylum: Series[str] = pa.Field(
        nullable=True,
        description="Phylum from taxonomic hierarchy; useful for AM vs EM rough filtering",
    )

    class Config:
        coerce = True
        strict = False
