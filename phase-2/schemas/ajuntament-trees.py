"""
Pandera schema for Ajuntament de Barcelona tree inventory (street + park combined).

Source: Arbrat Viari + Arbrat Zona CSV snapshots, Open Data BCN.
Seeded from observed data (189,090 rows, 22 columns from source; 23rd column
`source` added at concat time in notebook 01-data-profiling.ipynb).

DATA SHEET vs OBSERVED DISAGREEMENTS:
  - tipus_element: data sheet says "ARBRE / ARBRE EXEMPT / CONJUNT / PALMERA";
    observed: "ARBRE VIARI", "PALMERA VIARI" (street), "ARBRE ZONA", "PALMERA ZONA" (park).
  - categoria_arbrat: data sheet says tree category (street/park);
    observed: "EXEMPLAR", "PRIMERA", "SEGONA", "TERCERA" — size/quality classes.
  - Schema uses OBSERVED values. Data sheet will be updated in next revision.
"""

import pandera as pa
from pandera.typing import Series


class AjuntamentTreesSchema(pa.DataFrameModel):
    """One row = one tree at one snapshot. Public-realm census, not a sample."""

    # --- Identifiers ---
    codi: Series[str] = pa.Field(nullable=False, unique=True)

    # --- Coordinates (WGS84) ---
    latitud: Series[float] = pa.Field(
        nullable=False,
        ge=41.34,
        le=41.47,
        description="WGS84 latitude; bounds from BCN municipal extent",
    )
    longitud: Series[float] = pa.Field(
        nullable=False,
        ge=2.08,
        le=2.23,
        description="WGS84 longitude; bounds from BCN municipal extent",
    )

    # --- Coordinates (ETRS89 / UTM31N) ---
    x_etrs89: Series[float] = pa.Field(nullable=False)
    y_etrs89: Series[float] = pa.Field(nullable=False)

    # --- Element type (observed values) ---
    tipus_element: Series[str] = pa.Field(
        nullable=False,
        isin=["ARBRE VIARI", "PALMERA VIARI", "ARBRE ZONA", "PALMERA ZONA"],
    )

    # --- Green space (park trees only) ---
    espai_verd: Series[str] = pa.Field(
        nullable=True,
        description="Park or green space name; ~60% missing (all street trees)",
    )

    # --- Address ---
    adreca: Series[str] = pa.Field(
        nullable=True,
        description="Nearest street address; near-100% for street trees, sparse for park",
    )

    # --- Species ---
    cat_especie_id: Series[int] = pa.Field(nullable=False, ge=1)
    cat_nom_cientific: Series[str] = pa.Field(
        nullable=False,
        description="Scientific name; 0.01% genus-only (25 records), rest species-level",
    )
    cat_nom_castella: Series[str] = pa.Field(
        nullable=True,
        description="Castilian common name; ~2% missing",
    )
    cat_nom_catala: Series[str] = pa.Field(
        nullable=True,
        description="Catalan common name; ~2.2% missing",
    )

    # --- Management metadata ---
    categoria_arbrat: Series[str] = pa.Field(
        nullable=True,
        isin=["EXEMPLAR", "PRIMERA", "SEGONA", "TERCERA", None],
        description="Tree size/quality class; near-100% present. EXEMPLAR = heritage, PRIMERA = first-class.",
    )
    data_plantacio: Series[str] = pa.Field(
        nullable=True,
        description="Planting date (string, DD/MM/YYYY); 81% missing. Known anomalies: 28 future dates, 8 pre-1900.",
    )
    tipus_aigua: Series[str] = pa.Field(
        nullable=True,
        description="Irrigation water type; ~94% missing",
    )
    tipus_reg: Series[str] = pa.Field(
        nullable=True,
        isin=[
            "GOTEIG AVARIAT", "ASPERSIÓ", "DIFUSIÓ", "MÀNEGA",
            "SENSE INFORMAR", "GOTEIG", "ROTATOR", None,
        ],
        description="Irrigation method; near-100% present",
    )
    catalogacio: Series[str] = pa.Field(
        nullable=True,
        description="Cataloguing status; 99.5% missing",
    )

    # --- Administrative hierarchy ---
    codi_barri: Series[float] = pa.Field(
        nullable=True,
        description="Neighbourhood code; near-100% present",
    )
    nom_barri: Series[str] = pa.Field(
        nullable=True,
        description="Neighbourhood name; near-100% present",
    )
    codi_districte: Series[float] = pa.Field(
        nullable=True,
        ge=1,
        le=10,
        description="District code (1–10); 6 records with invalid codes observed in full dataset",
    )
    nom_districte: Series[str] = pa.Field(
        nullable=True,
        isin=[
            "CIUTAT VELLA", "EIXAMPLE", "SANTS - MONTJUÏC",
            "LES CORTS", "SARRIÀ - SANT GERVASI", "GRÀCIA",
            "HORTA - GUINARDÓ", "NOU BARRIS", "SANT ANDREU", "SANT MARTÍ",
        ],
    )

    # --- Geometry WKT (present in portal export; may be absent in other formats) ---
    geom: Series[str] = pa.Field(
        nullable=True,
        description="WKT geometry string; present in CSV portal export",
    )

    class Config:
        coerce = True
        strict = False
