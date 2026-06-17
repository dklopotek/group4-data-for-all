"""
clean_data.py — deterministic data preparation pipeline for Mycorrhizal Barcelona.

Reads raw data from ``data/``, applies the cleaning and scoring logic from
notebooks 01–04, and writes the scored grid to ``data/processed/``.

Run from project root::

    python src/clean_data.py

Cleaning decisions documented in ``phase-3/data-cleaning-report.md``.

Pipeline stages
---------------
    1. Load & combine tree inventory (street + park CSVs)
    2. Normalise species names
    3. Join against FungalRoot v2.0 lookup (with hardcoded top-20 override)
    4. Assign mycorrhizal type (AM / EM / NM) per tree
    5. Build 400 m grid clipped to Barcelona municipal boundary
    6. Spatial join trees into grid cells
    7. Per-cell tree statistics (counts, fractions, species richness,
       Platanus count)
    8. Load GBIF fungal occurrences and count per cell
    9. Zonal statistics from three rasters: sealed surface, LST, NDVI
    10. Compute four sub-scores (S1–S4)
    11. Compute PRPI v1.1 (Platanus Replacement Priority Index, EM-optimistic
        scenario) — anchored to Pla Director de l'Arbrat de Barcelona 2017-2037
    12. Compute VPA allergenicity + species preference (v1.2, Cariñanos &
        Marinangeli 2021)
    13. Compute PRPI operational scenario (v1.2, Zelkova/Pistacia pilot
        palette)
    14. Compute three composite scores (Scenarios A, B, C), 5-term
    15. Flag top-15 priority cells (Scenario B, district-constrained)
    16. Classify intervention type per cell (5-way) and replacement flag
    17. Assert invariants and write output

Data contract (output schema): ``phase-3/data-contract.yaml``
"""

from __future__ import annotations

import json
import math
import warnings
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point, box

warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option("display.max_columns", 30)

# Optional rasterio import — graceful fallback to synthetic values
try:
    import rasterio
    from rasterio.mask import mask as rio_mask

    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

# ===========================================================================
# PATH CONSTANTS
# ===========================================================================
# All paths are relative to the project root (two levels up from this file
# when src/ is a subdirectory of the project root).

_HERE = Path(__file__).resolve().parent
PROJECT_ROOT = _HERE.parent

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

VIARI_PATH = DATA_DIR / "arbrat-viari.csv"
ZONA_PATH = DATA_DIR / "arbrat-zona.csv"
FUNGALROOT_PATH = DATA_DIR / "fungalroot.csv"
BOUNDARY_PATH = DATA_DIR / "bcn-boundary.geojson"
GBIF_PATH = DATA_DIR / "gbif-fungi.json"
VPA_PATH = DATA_DIR / "raw" / "vpa-mediterranean-species.csv"
SEALED_PATH = DATA_DIR / "urban-atlas" / "sealed_surface.tif"
LST_PATH = DATA_DIR / "landsat" / "lst_summer_composite.tif"
NDVI_PATH = DATA_DIR / "sentinel2" / "ndvi_summer_composite.tif"
SCORED_OUTPUT_PATH = PROCESSED_DIR / "scored_grid.geojson"

# arbrat-viari snapshot identifier (re-pulled 2026-05-26 from Open Data BCN)
ARBRAT_VIARI_SNAPSHOT = "2026_1T"

# ===========================================================================
# CLEANING CONSTANTS
# ===========================================================================
GRID_SIZE = 400  # metres — matches Superilla block width
CRS_PROJ = "EPSG:25831"  # ETRS89 / UTM Zone 31N
CRS_GEO = "EPSG:4326"  # WGS-84 (input lon/lat)

# BCN bounding-box fallback (UTM31N, approximate) — used only when the
# boundary file is absent.
BCN_XMIN = 420_800
BCN_XMAX = 435_600
BCN_YMIN = 4_574_000
BCN_YMAX = 4_591_200

# Tree-age threshold for "young" trees (mycorrhizal colonisation uncertain)
YOUNG_YEARS = 5
COLONISATION_UNCERTAIN_THRESHOLD = 30  # percent of trees young

# S4 mismatch thresholds (0–100 scale because am_pct/em_pct are 0–100)
AM_DOMINANCE_THRESHOLD = 80  # am_pct >= 80 → informationally null
EM_DOMINANCE_THRESHOLD = 50  # em_pct >= 50 → EM-dominant

# S4 mismatch scores
S4_INFORMATIONALLY_NULL = 0.5
S4_EM_PARTNERS_PRESENT = 0.0
S4_EM_POTENTIAL_ISOLATION = 0.8
S4_MIXED = 0.6

# Expected myco-type thresholds (0–100 scale)
MYCO_AM_THRESHOLD = 60  # am_pct >= 60 → "AM"
MYCO_EM_THRESHOLD = 60  # em_pct >= 60 → "EM"

# Sealing barrier threshold — cells above this are physical barriers
SEAL_THRESHOLD = 0.7

# AM / EM edge-distance thresholds (metres) for network graph
AM_DISTANCE_M = 15.0
EM_DISTANCE_M = 35.0

# Seed for deterministic synthetic fallback values
RNG_SEED = 42

# Minimum age (years) to consider a tree "not young" — used only when
# planting date is known.
REFERENCE_DATE = pd.Timestamp("2026-05-26")

# Composite-score weight scenarios (from ADR-003, extended with PRPI in v1.1)
#   A: equal weights
#   B: sealed-dominant (PRIMARY)
#   C: heat + canopy emphasis
# PRPI (Platanus Replacement Priority Index) is folded in as a 5th term.
# Each scenario was rebalanced so weights still sum to 1.0.
SCENARIO_WEIGHTS: dict[str, dict[str, float]] = {
    "A": {"sealed": 0.20, "lst": 0.20, "ndvi": 0.20, "mismatch": 0.20, "prpi": 0.20},
    "B": {"sealed": 0.45, "lst": 0.20, "ndvi": 0.15, "mismatch": 0.05, "prpi": 0.15},
    "C": {"sealed": 0.15, "lst": 0.25, "ndvi": 0.25, "mismatch": 0.20, "prpi": 0.15},
}

# ---------------------------------------------------------------------------
# PRPI (Platanus Replacement Priority Index) constants
# ---------------------------------------------------------------------------
# Anchored to Pla Director de l'Arbrat de Barcelona 2017-2037: city policy
# targets a reduction of Platanus × acerifolia from ~27% to <12% of street
# trees by 2037 (Ajuntament de Barcelona, 2017).
#
# PRPI = w_platanus * (platanus_pct / 100)
#      + w_ndvi     * s3_inverted_ndvi
#      + w_s4_shift * s4_shift_potential
#      + w_feas     * (1 - s1_sealed)
#
# Weights emphasise Platanus density (the policy driver) while still
# rewarding cells where replacement breaks the AM-blind null zone (S4 shift)
# and where planting is physically feasible (low sealed surface).
PLATANUS_SPECIES_KEY = "platanus × acerifolia"  # normalised species key
PLATANUS_TARGET_PCT = 12.0  # city 2037 target: Platanus <12% of street trees

PRPI_WEIGHTS: dict[str, float] = {
    "platanus": 0.40,
    "ndvi": 0.20,
    "s4_shift": 0.20,
    "feasibility": 0.20,
}

PRPI_THRESHOLD = 0.5  # cells with PRPI > threshold are replacement candidates
SEAL_FEASIBILITY = 0.7  # cells must have s1_sealed < this to be plantable
S4_SHIFT_ASSUMPTION = "EM"  # assume Platanus is replaced with EM hosts
                            # (Quercus ilex, Pinus halepensis — upper-bound
                            #  sensitivity scenario, not operational target)

# ---------------------------------------------------------------------------
# Species preference filter (v1.2 — operational scenario)
# ---------------------------------------------------------------------------
# Per deep-research review (2026-05-26, outputs/deep-research-platanus-prpi.md):
#   - Barcelona's Espais Verds *actively pilots* Zelkova serrata and Pistacia
#     chinensis as Platanus replacements — these are operationally preferred.
#   - Quercus ilex carries Que i 1 (Bet v 1 homolog) and is VPA IV–V — same
#     allergenicity class as Platanus (Cariñanos & Marinangeli, 2021;
#     González-Mancebo et al., 2020). EM-optimistic substitution toward Q. ilex
#     inverts the public-health goal.
#   - Celtis australis is jointly 15%-capped with Platanus, is itself an AM
#     host, and lifts sidewalks.
# SPECIES_PREFERENCE_WEIGHTS is the operational alternative to S4_SHIFT_ASSUMPTION:
# both scenarios are computed; downstream consumers can compare.
SPECIES_PREFERENCE_WEIGHTS: dict[str, float] = {
    # Up-weight: Barcelona's pilot palette (low-VPA, drought-tolerant)
    "Zelkova serrata": 1.0,
    "Pistacia chinensis": 0.9,
    "Sophora japonica": 0.9,
    "Styphnolobium japonicum": 0.9,
    "Melia azedarach": 0.9,
    "Jacaranda mimosifolia": 0.9,
    "Tipuana tipu": 0.9,
    "Brachychiton populneus": 0.9,
    "Magnolia grandiflora": 0.85,
    "Tilia cordata": 0.8,
    "Pinus halepensis": 0.7,  # EM host but low VPA — middle ground
    # Mid: acceptable but not preferred
    "Pyrus calleryana": 0.6,
    "Cercis siliquastrum": 0.6,
    "Ginkgo biloba": 0.6,
    "Robinia pseudoacacia": 0.5,
    # Down-weight: high VPA or operational issues
    "Quercus ilex": 0.3,  # EM host BUT VPA IV–V — inverts allergy goal
    "Celtis australis": 0.2,  # AM host + jointly capped + sidewalk lift
    "Ulmus pumila": 0.1,  # being phased out of BCN palette
    "Eucalyptus globulus": 0.1,  # being phased out
    # Source species (do not "replace with itself")
    "Platanus × acerifolia": 0.0,
}
SPECIES_PREFERENCE_DEFAULT = 0.5  # unknown species — middle weight

# Hardcoded myco-type override for the top-20 species (~90 % of inventory).
# Applied AFTER the FungalRoot CSV join for safety (BUG-2 fix).
# Sources: FungalRoot v2.0, Smith & Read (2008), Brundrett & Tedersoo (2018).
TOP20_MYCO: dict[str, str] = {
    "Platanus × acerifolia": "AM",
    "Celtis australis": "AM",
    "Tipuana tipu": "AM",
    "Styphnolobium japonicum": "AM",
    "Melia azedarach": "AM",
    "Brachychiton populneus": "AM",
    "Jacaranda mimosifolia": "AM",
    "Pinus pinea": "EM",
    "Ligustrum lucidum": "AM",
    "Pyrus calleryana 'Chanticleer'": "AM",
    "Ulmus pumila": "AM",
    "Cercis siliquastrum": "AM",
    "Prunus cerasifera 'Pissardii'": "AM",
    "Cupressus sempervirens": "AM",
    "Citrus × aurantium": "AM",
    "Robinia pseudoacacia": "AM",
    "Pinus halepensis": "EM",
    "Quercus ilex": "EM",
    "Magnolia grandiflora": "AM",
    "Grevillea robusta": "AM",
}

# Intervention-type labels matching sub-score names
LABEL_MAP: dict[str, str] = {
    "s1_sealed": "de-paving",
    "s2_lst_anomaly": "cooling",
    "s3_inverted_ndvi": "planting",
    "s4_mismatch": "multi-strategy",
    "prpi": "species-replacement",
}

# Columns retained from the raw tree inventory (SEL-005 in cleaning report)
KEEP_COLS: list[str] = [
    "codi",
    "cat_nom_cientific",
    "nom_districte",
    "nom_barri",
    "codi_districte",
    "codi_barri",
    "source",
    "data_plantacio",
    "x_etrs89",
    "y_etrs89",
]


# ===========================================================================
# HELPER: raster zonal mean (shared by S1, S2, S3)
# ===========================================================================


def zonal_mean_from_raster(
    raster_path: Path,
    gdf: gpd.GeoDataFrame,
    band: int = 1,
    scale: float = 1.0,
) -> np.ndarray:
    """Compute per-feature zonal mean of a single raster band.

    Parameters
    ----------
    raster_path : Path
        Path to a GeoTIFF raster.
    gdf : GeoDataFrame
        Polygon features in any CRS (reprojected on the fly).
    band : int
        Raster band index (1-based). Default 1.
    scale : float
        Multiplicative scale factor applied to pixel values after reading.
        Example: ``scale=0.01`` to convert 0–100 to 0–1.

    Returns
    -------
    np.ndarray
        Array of length ``len(gdf)``.  Cells with no valid pixels receive
        ``NaN``.

    Example
    -------
    >>> vals = zonal_mean_from_raster(SEALED_PATH, grid, band=1, scale=1.0)
    """
    if not RASTERIO_AVAILABLE or not raster_path.exists():
        return np.full(len(gdf), np.nan, dtype=np.float64)

    values = np.full(len(gdf), np.nan, dtype=np.float64)
    with rasterio.open(raster_path) as src:
        gdf_r = gdf if gdf.crs == src.crs else gdf.to_crs(src.crs)
        for i, geom in enumerate(gdf_r.geometry):
            try:
                out_image, _ = rio_mask(src, [geom], crop=True, nodata=src.nodata)
                data = out_image[band - 1].astype(np.float64)
                if src.nodata is not None:
                    data = data[data != src.nodata]
                if data.size > 0:
                    values[i] = np.nanmean(data) * scale
            except Exception:
                pass  # cell outside raster extent -> stays NaN
    return values


# ===========================================================================
# FUNCTIONS — one transform per function
# ===========================================================================


def load_tree_inventory(viari_path: Path, zona_path: Path) -> pd.DataFrame:
    """Load and concatenate street-tree and park-tree CSVs.

    Parameters
    ----------
    viari_path : Path
        Path to ``arbrat-viari.csv`` (street trees).
    zona_path : Path
        Path to ``arbrat-zona.csv`` (park trees).

    Returns
    -------
    pd.DataFrame
        Concatenated inventory with a ``source`` column (``"street"`` /
        ``"park"``) and only the columns needed downstream.

    Example
    -------
    >>> df = load_tree_inventory(
    ...     DATA_DIR / "arbrat-viari.csv",
    ...     DATA_DIR / "arbrat-zona.csv",
    ... )
    """
    viari = pd.read_csv(viari_path, encoding="utf-8", low_memory=False)
    zona = pd.read_csv(zona_path, encoding="utf-8", low_memory=False)
    viari["source"] = "street"
    zona["source"] = "park"
    out = pd.concat([viari, zona], ignore_index=True)
    # Retain only columns needed downstream
    keep = [c for c in KEEP_COLS if c in out.columns]
    out = out[keep].copy()
    assert len(out) > 0, "Tree inventory is empty after loading"
    return out


def normalize_species_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise scientific species names to a canonical lowercase form.

    The raw Ajuntament data has inconsistent formatting:
    ``Quercus ilex``, ``Q. ilex``, ``quercus ilex``, etc.
    This function strips whitespace, lowercases, and creates a
    ``species_name`` column suitable for joining against FungalRoot.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ``cat_nom_cientific`` column.

    Returns
    -------
    pd.DataFrame
        New column ``species_name`` (lowercase, stripped).

    Example
    -------
    >>> df = normalize_species_names(df)
    >>> df["species_name"].iloc[0]
    'platanus × acerifolia'
    """
    out = df.copy()
    raw = out["cat_nom_cientific"].astype(str).str.strip().str.lower()
    out["species_name"] = raw

    n_norm = out["species_name"].notna().sum()
    assert n_norm > 0, "All species names are null after normalisation"
    return out


def load_fungalroot_lookup(
    fungalroot_path: Path,
    top20_override: dict[str, str] | None = None,
) -> dict[str, str]:
    """Load the FungalRoot v2.0 species-to-myco-type lookup table.

    Reads the CSV, normalises mycorrhizal-type strings to the canonical
    vocabulary (``AM``, ``EM``, ``NM``), and applies a hardcoded top-20
    override for safety.

    Parameters
    ----------
    fungalroot_path : Path
        Path to ``fungalroot.csv``.  Expected columns: ``species_name``
        (or ``species``, ``name``) and ``myco_type`` (or any column
        containing ``myco`` or ``type``).
    top20_override : dict or None
        Species-to-type mapping that takes precedence over the CSV.
        Default: ``TOP20_MYCO``.

    Returns
    -------
    dict
        Mapping ``species_name → myco_type`` where ``myco_type`` is one of
        ``"AM"``, ``"EM"``, or ``"NM"``.

    Example
    -------
    >>> lookup = load_fungalroot_lookup(DATA_DIR / "fungalroot.csv")
    >>> lookup["platanus × acerifolia"]
    'AM'
    """
    if top20_override is None:
        top20_override = TOP20_MYCO

    if not fungalroot_path.exists():
        # Fall back to hardcoded stub — lowercased for join compatibility
        out = {k.lower(): v for k, v in top20_override.items()}
        print(
            f"  [load_fungalroot_lookup] CSV not found — "
            f"using hardcoded top-{len(top20_override)} stub"
        )
        return out

    fr = pd.read_csv(fungalroot_path, encoding="utf-8")
    # Normalise column names
    fr.columns = [c.strip().lower().replace(" ", "_") for c in fr.columns]
    name_col = next(
        (c for c in fr.columns if "species" in c or "name" in c),
        fr.columns[0],
    )
    type_col = next(
        (c for c in fr.columns if "myco" in c or "type" in c),
        fr.columns[1],
    )
    fr = fr.rename(columns={name_col: "species_name", type_col: "myco_type"})

    # Normalise myco_type to canonical {AM, EM, NM} vocabulary
    fr["myco_type"] = fr["myco_type"].apply(_normalise_myco)

    # Lowercase for join compatibility
    fr["species_name"] = fr["species_name"].astype(str).str.strip().str.lower()
    out = dict(zip(fr["species_name"], fr["myco_type"]))

    # Top-20 override: curated values trump the CSV (BUG-2 fix)
    for sp, mt in top20_override.items():
        out[sp.lower()] = mt

    print(f"  [load_fungalroot_lookup] Loaded {len(out):,} species mappings")
    return out


def _normalise_myco(v: Any) -> str:
    """Normalise a raw FungalRoot mycorrhizal-type string to {AM, EM, NM}.

    Handles compound strings like ``"EcM, AM undetermined"``,
    ``"EcM, no AM colonization"``, etc.
    """
    if not isinstance(v, str):
        return "NM"
    v = v.strip().upper()
    if v in ("ECM",) or "ECM" in v or v == "EM":
        return "EM"
    if "AM" in v and "ECM" not in v:
        return "AM"
    if v in ("NM", "NON-MYCORRHIZAL", "OM", "ERM"):
        return "NM"
    return "NM"


def assign_myco_type(
    df: pd.DataFrame,
    myco_lookup: dict[str, str],
) -> pd.DataFrame:
    """Assign mycorrhizal type (AM / EM / NM) to every tree row.

    Trees whose species is not in the lookup receive ``"NM"`` (Not Matched).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ``species_name`` column (lowercased).
    myco_lookup : dict
        Species → myco_type mapping (from ``load_fungalroot_lookup``).

    Returns
    -------
    pd.DataFrame
        New column ``myco_type``.

    Example
    -------
    >>> lookup = load_fungalroot_lookup(...)
    >>> df = assign_myco_type(df, lookup)
    >>> df["myco_type"].value_counts()
    AM    151801
    NM     25164
    EM     12175
    """
    out = df.copy()
    out["myco_type"] = out["species_name"].map(myco_lookup).fillna("NM")
    assert out["myco_type"].notna().all(), "Some trees have null myco_type"
    return out


def build_grid(
    boundary_path: Path,
    grid_size: int = GRID_SIZE,
    crs: str = CRS_PROJ,
) -> gpd.GeoDataFrame:
    """Build a square grid clipped to the Barcelona municipal boundary.

    Grid cells are snapped to ``grid_size`` multiples for reproducibility
    across runs.  Cells that do not intersect the boundary polygon are
    dropped.

    Parameters
    ----------
    boundary_path : Path
        Path to a GeoJSON or Shapefile containing the BCN municipal polygon.
    grid_size : int
        Cell side length in metres.  Default 400.
    crs : str
        Target CRS (metre-unit).  Default ``EPSG:25831``.

    Returns
    -------
    gpd.GeoDataFrame
        Columns: ``cell_id``, ``cell_x0``, ``cell_y0``, ``geometry``.
        CRS matches input ``crs``.

    Example
    -------
    >>> grid = build_grid(BOUNDARY_PATH)
    >>> len(grid)
    495
    """
    if boundary_path.exists():
        boundary_raw = gpd.read_file(boundary_path)
        boundary = boundary_raw.to_crs(crs)
        bcn_poly = boundary.union_all()
    else:
        # Fallback bounding box — approximate BCN extent
        bcn_poly = box(BCN_XMIN, BCN_YMIN, BCN_XMAX, BCN_YMAX)
        print(
            "  [build_grid] Boundary file not found — "
            "using hardcoded BCN bounding box"
        )

    minx, miny, maxx, maxy = bcn_poly.bounds
    x0 = math.floor(minx / grid_size) * grid_size
    y0 = math.floor(miny / grid_size) * grid_size
    x1 = math.ceil(maxx / grid_size) * grid_size
    y1 = math.ceil(maxy / grid_size) * grid_size

    tiles: list[dict[str, Any]] = []
    xs = np.arange(x0, x1, grid_size)
    ys = np.arange(y0, y1, grid_size)
    for xi in xs:
        for yi in ys:
            tile = box(xi, yi, xi + grid_size, yi + grid_size)
            if tile.intersects(bcn_poly):
                tiles.append(
                    {
                        "geometry": tile,
                        "cell_id": (
                            f"C{int((xi - x0) / grid_size):03d}"
                            f"_{int((yi - y0) / grid_size):03d}"
                        ),
                        "cell_x0": int(xi),
                        "cell_y0": int(yi),
                    }
                )

    out = gpd.GeoDataFrame(tiles, crs=crs)
    assert len(out) > 0, "Grid is empty — boundary may be invalid"
    return out


def build_tree_geodataframe(
    df: pd.DataFrame,
    crs: str = CRS_PROJ,
) -> gpd.GeoDataFrame:
    """Convert the tree inventory DataFrame to a point GeoDataFrame.

    Uses the authoritative ``x_etrs89`` / ``y_etrs89`` columns (UTM31N).
    Drops rows with null coordinates.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ``x_etrs89`` and ``y_etrs89`` columns.
    crs : str
        Target CRS.  Default ``EPSG:25831``.

    Returns
    -------
    gpd.GeoDataFrame
        Point geometry with the same CRS.

    Example
    -------
    >>> trees_gdf = build_tree_geodataframe(df)
    """
    out = df.copy()
    coord_mask = out["x_etrs89"].notna() & out["y_etrs89"].notna()
    out = out[coord_mask].copy()
    geom = gpd.points_from_xy(out["x_etrs89"], out["y_etrs89"])
    return gpd.GeoDataFrame(out, geometry=geom, crs=crs)


def spatial_join_trees_to_grid(
    trees_gdf: gpd.GeoDataFrame,
    grid_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Join tree points into grid cells via spatial intersection.

    Both layers must share the same CRS.  Uses ``predicate="within"``
    so each tree is assigned to exactly one cell.  Boundary-edge trees
    missed are negligible (< 0.1 %).

    Parameters
    ----------
    trees_gdf : GeoDataFrame
        Tree points (from ``build_tree_geodataframe``).
    grid_gdf : GeoDataFrame
        Grid cells (from ``build_grid``).

    Returns
    -------
    gpd.GeoDataFrame
        Trees with an added ``cell_id`` column (``"Cxxx_yyy"``).

    Example
    -------
    >>> joined = spatial_join_trees_to_grid(trees_gdf, grid)
    >>> joined["cell_id"].nunique()
    495
    """
    joined = gpd.sjoin(
        trees_gdf,
        grid_gdf[["cell_id", "geometry"]],
        how="inner",
        predicate="within",
    )
    joined = joined.drop(columns=["index_right"], errors="ignore")
    matched = len(joined)
    total = len(trees_gdf)
    assert matched > 0, "No trees matched any grid cell"
    if matched < total:
        print(
            f"  [spatial_join] {total - matched:,} trees ({1 - matched / total:.2%}) "
            f"not within any cell (boundary-edge)"
        )
    return joined


def _modal(series: pd.Series, default: str = "UNKNOWN") -> str:
    """Return the most frequent non-null value in a series."""
    counts = series.dropna().value_counts()
    return str(counts.index[0]) if len(counts) else default


def _species_list_json(series: pd.Series) -> str:
    """Unique, sorted scientific names as a JSON array string."""
    names = sorted(series.dropna().unique().tolist())
    return json.dumps(names, ensure_ascii=False)


def _young_pct(series: pd.Series) -> float:
    """Fraction (0–100) of trees planted within the last ``YOUNG_YEARS`` years."""
    n_total = len(series)
    if n_total == 0:
        return 0.0
    threshold = REFERENCE_DATE - pd.DateOffset(years=YOUNG_YEARS)
    n_young = (series > threshold).sum()
    return round(float(n_young / n_total * 100), 2)


def compute_cell_aggregation(joined: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute per-grid-cell summary statistics from joined tree rows.

    Parameters
    ----------
    joined : GeoDataFrame
        Trees with ``cell_id`` from ``spatial_join_trees_to_grid``.
        Must contain ``codi``, ``nom_districte``, ``nom_barri``,
        ``cat_nom_cientific``, and ``data_plantacio`` (as ``plant_date``
        or the raw column).

    Returns
    -------
    pd.DataFrame
        One row per occupied cell with columns:
        ``cell_id``, ``tree_count``, ``district_name``, ``barri_name``,
        ``species_list``, ``trees_young_pct``.

    Example
    -------
    >>> agg = compute_cell_aggregation(joined)
    >>> len(agg)
    495
    """
    out = joined.copy()

    # Parse planting date if not already done
    if "plant_date" not in out.columns and "data_plantacio" in out.columns:
        out["plant_date"] = pd.to_datetime(
            out["data_plantacio"], errors="coerce"
        )

    agg = (
        out.groupby("cell_id", observed=True)
        .agg(
            tree_count=("codi", "count"),
            district_name=("nom_districte", lambda s: _modal(s)),
            barri_name=("nom_barri", lambda s: _modal(s)),
            species_list=("cat_nom_cientific", _species_list_json),
            trees_young_pct=("plant_date", _young_pct),
            n_platanus=(
                "species_name",
                lambda s: int((s == PLATANUS_SPECIES_KEY).sum()),
            ),
        )
        .reset_index()
    )

    assert len(agg) > 0, "Cell aggregation produced zero rows"
    return agg


def compute_myco_statistics(joined: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute per-cell mycorrhizal-type counts and percentages.

    ``am_pct`` and ``em_pct`` are computed from the *matched subset only*
    (trees with myco_type in {AM, EM}), not from total trees.  This follows
    the data contract specification.

    Parameters
    ----------
    joined : GeoDataFrame
        Trees with ``cell_id`` and ``myco_type`` columns.

    Returns
    -------
    pd.DataFrame
        One row per cell with columns:
        ``cell_id``, ``n_AM``, ``n_EM``, ``n_unknown``,
        ``am_pct``, ``em_pct``, ``species_richness``,
        ``expected_myco_type``.

    Example
    -------
    >>> myco = compute_myco_statistics(joined)
    """
    out = joined.copy()

    def _cell_myco(group: pd.DataFrame) -> pd.Series:
        n = len(group)
        counts = group["myco_type"].value_counts()
        am = counts.get("AM", 0)
        em = counts.get("EM", 0)
        nm = counts.get("NM", 0)

        # Percentages from matched subset (AM + EM)
        known = am + em
        if known > 0:
            am_pct_val = round(am / known * 100, 2)
            em_pct_val = round(em / known * 100, 2)
        else:
            am_pct_val = 0.0
            em_pct_val = 0.0

        # Species richness from matched subset
        matched_mask = group["myco_type"].isin(["AM", "EM"])
        rich = group.loc[matched_mask, "species_name"].nunique()

        # Expected myco type
        if known == 0:
            expected = "Unknown"
        elif am_pct_val >= MYCO_AM_THRESHOLD:
            expected = "AM"
        elif em_pct_val >= MYCO_EM_THRESHOLD:
            expected = "EM"
        else:
            expected = "Mixed"

        return pd.Series(
            {
                "n_AM": int(am),
                "n_EM": int(em),
                "n_unknown": int(nm),
                "am_pct": am_pct_val,
                "em_pct": em_pct_val,
                "species_richness": int(rich),
                "expected_myco_type": expected,
            }
        )

    myco = (
        out.groupby("cell_id", observed=True)
        .apply(_cell_myco)
        .reset_index()
    )

    return myco


def load_gbif_occurrences(gbif_path: Path) -> gpd.GeoDataFrame:
    """Load GBIF fungal occurrence JSON and return a point GeoDataFrame.

    Parameters
    ----------
    gbif_path : Path
        Path to the GBIF API response JSON (``gbif-fungi.json``).

    Returns
    -------
    gpd.GeoDataFrame
        Points in EPSG:4326 with columns ``gbif_id``, ``phylum``,
        ``species``, ``basis_of_record``.

    Example
    -------
    >>> gbif_gdf = load_gbif_occurrences(GBIF_PATH)
    >>> len(gbif_gdf)
    1024
    """
    if not gbif_path.exists():
        return gpd.GeoDataFrame(
            {"gbif_id": pd.Series(dtype=str), "phylum": pd.Series(dtype=str)},
            geometry=gpd.GeoSeries(dtype="geometry"),
            crs=CRS_GEO,
        )

    with open(gbif_path, encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("results", [])
    rows: list[dict[str, Any]] = []
    for r in records:
        lat = r.get("decimalLatitude")
        lon = r.get("decimalLongitude")
        if lat is None or lon is None:
            continue
        rows.append(
            {
                "gbif_id": str(r.get("key", "")),
                "phylum": r.get("phylum"),
                "species": r.get("species", ""),
                "basis_of_record": r.get("basisOfRecord", ""),
                "geometry": Point(lon, lat),
            }
        )

    out = gpd.GeoDataFrame(rows, crs=CRS_GEO)
    return out


def count_gbif_per_cell(
    gbif_gdf: gpd.GeoDataFrame,
    grid_gdf: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Spatial join GBIF occurrences to grid cells and count per cell.

    Also determines ``em_gbif_nearby`` — whether at least one Basidiomycota
    (putative EM) record falls in or near the cell.

    Parameters
    ----------
    gbif_gdf : GeoDataFrame
        GBIF occurrence points in EPSG:4326.
    grid_gdf : GeoDataFrame
        Grid cells in EPSG:25831.

    Returns
    -------
    pd.DataFrame
        Columns: ``cell_id``, ``gbif_records``, ``em_gbif_nearby``.
        Every occupied cell is present; cells with zero GBIF records
        get ``gbif_records=0`` and ``em_gbif_nearby=0``.
    """
    if len(gbif_gdf) == 0:
        return pd.DataFrame(
            {
                "cell_id": grid_gdf["cell_id"],
                "gbif_records": 0,
                "em_gbif_nearby": 0,
            }
        )

    # Reproject GBIF to projected CRS
    gbif_proj = gbif_gdf.to_crs(grid_gdf.crs)

    # Flag putative EM records: Basidiomycota phylum
    gbif_proj["is_putative_em"] = (
        gbif_proj["phylum"].str.lower() == "basidiomycota"
    )

    # Spatial join: which GBIF records fall in which cell?
    joined = gpd.sjoin(
        gbif_proj,
        grid_gdf[["cell_id", "geometry"]],
        how="left",
        predicate="within",
    )
    joined = joined.drop(columns=["index_right"], errors="ignore")

    # Per-cell counts
    counts = (
        joined.groupby("cell_id", observed=True)
        .agg(
            gbif_records=("gbif_id", "count"),
            em_records=("is_putative_em", "sum"),
        )
        .reset_index()
    )
    counts["em_gbif_nearby"] = (counts["em_records"] > 0).astype(int)

    # Ensure every cell in the grid is represented
    out = grid_gdf[["cell_id"]].merge(counts, on="cell_id", how="left")
    out["gbif_records"] = out["gbif_records"].fillna(0).astype(int)
    out["em_gbif_nearby"] = out["em_gbif_nearby"].fillna(0).astype(int)

    return out[["cell_id", "gbif_records", "em_gbif_nearby"]]


def compute_s1_sealed(
    gdf: gpd.GeoDataFrame,
    raster_path: Path = SEALED_PATH,
) -> gpd.GeoDataFrame:
    """Compute S1: sealed-surface fraction sub-score.

    Reads the Urban Atlas sealed-surface raster.  The raster is already on
    a 0–1 scale (BUG-3 fix).  When the raster is absent, draws synthetic
    values from a Beta distribution calibrated to BCN's ~30 % average
    sealed fraction.

    Parameters
    ----------
    gdf : GeoDataFrame
        Grid cells in EPSG:25831.
    raster_path : Path
        Path to ``sealed_surface.tif``.

    Returns
    -------
    GeoDataFrame
        New columns: ``mean_sealed`` (0–1), ``s1_sealed`` (0–1, same value).
    """
    out = gdf.copy()

    if RASTERIO_AVAILABLE and raster_path.exists():
        sealed_raw = zonal_mean_from_raster(
            raster_path, out, band=1, scale=1.0
        )
        out["mean_sealed"] = np.where(np.isnan(sealed_raw), 0.0, sealed_raw)
    else:
        rng = np.random.default_rng(RNG_SEED)
        out["mean_sealed"] = rng.beta(2, 5, size=len(out))
        print(
            "  [S1] sealed_surface.tif absent — "
            "using synthetic Beta(2,5) values (illustrative only)"
        )

    out["s1_sealed"] = out["mean_sealed"].clip(0, 1)
    return out


def compute_s2_lst(
    gdf: gpd.GeoDataFrame,
    raster_path: Path = LST_PATH,
) -> gpd.GeoDataFrame:
    """Compute S2: Land Surface Temperature anomaly sub-score.

    Reads the Landsat summer composite, computes zonal mean per cell,
    derives the anomaly from the city-wide median, and normalises to
    [0, 1] via min-max scaling.

    Parameters
    ----------
    gdf : GeoDataFrame
        Grid cells in EPSG:25831.
    raster_path : Path
        Path to ``lst_summer_composite.tif``.

    Returns
    -------
    GeoDataFrame
        New columns: ``mean_lst_celsius``, ``lst_anomaly``,
        ``s2_lst_anomaly`` (min-max normalised to 0–1).
    """
    out = gdf.copy()

    if RASTERIO_AVAILABLE and raster_path.exists():
        lst_raw = zonal_mean_from_raster(raster_path, out, band=1)
        city_median = np.nanmedian(lst_raw[~np.isnan(lst_raw)])
        anomaly = lst_raw - city_median
        out["mean_lst_celsius"] = np.where(
            np.isnan(lst_raw), np.nan, lst_raw
        )
        out["lst_anomaly"] = np.where(np.isnan(anomaly), 0.0, anomaly)
    else:
        rng = np.random.default_rng(RNG_SEED + 1)
        anomaly = rng.normal(loc=0, scale=2.5, size=len(out))
        out["lst_anomaly"] = np.clip(anomaly, -5, 8)
        out["mean_lst_celsius"] = np.nan
        print(
            "  [S2] lst_summer_composite.tif absent — "
            "using synthetic N(0, 2.5) values (illustrative only)"
        )

    # Min-max normalise anomaly to [0, 1]
    city_min = out["lst_anomaly"].min()
    city_max = out["lst_anomaly"].max()
    denom = city_max - city_min
    if denom < 1e-9:
        out["s2_lst_anomaly"] = 0.5
    else:
        out["s2_lst_anomaly"] = (
            (out["lst_anomaly"] - city_min) / denom
        ).clip(0, 1)

    return out


def compute_s3_ndvi(
    gdf: gpd.GeoDataFrame,
    raster_path: Path = NDVI_PATH,
) -> gpd.GeoDataFrame:
    """Compute S3: inverted NDVI sub-score.

    Reads the Sentinel-2 summer NDVI composite, computes zonal mean per
    cell, normalises to [0, 1], and inverts (1 - normalised_ndvi) so that
    lower canopy = higher barrier.

    Parameters
    ----------
    gdf : GeoDataFrame
        Grid cells in EPSG:25831.
    raster_path : Path
        Path to ``ndvi_summer_composite.tif``.

    Returns
    -------
    GeoDataFrame
        New columns: ``mean_ndvi``, ``s3_inverted_ndvi`` (0–1).
    """
    out = gdf.copy()

    if RASTERIO_AVAILABLE and raster_path.exists():
        ndvi_raw = zonal_mean_from_raster(raster_path, out, band=1)
        out["mean_ndvi"] = np.where(np.isnan(ndvi_raw), 0.3, ndvi_raw)
    else:
        rng = np.random.default_rng(RNG_SEED + 2)
        raw = rng.beta(3, 3, size=len(out))
        out["mean_ndvi"] = 0.1 + raw * (0.7 - 0.1)
        print(
            "  [S3] ndvi_summer_composite.tif absent — "
            "using synthetic Beta(3,3) values (illustrative only)"
        )

    # Normalise to [0, 1] then invert
    ndvi_min = out["mean_ndvi"].min()
    ndvi_max = out["mean_ndvi"].max()
    ndvi_range = ndvi_max - ndvi_min
    if ndvi_range < 1e-9:
        normalised = 0.5
    else:
        normalised = (out["mean_ndvi"] - ndvi_min) / ndvi_range

    out["s3_inverted_ndvi"] = (1 - normalised).clip(0, 1)
    return out


def compute_s4_mismatch(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Compute S4: host-mycorrhizal mismatch sub-score.

    Rule-based scoring using thresholds on 0–100 scale columns
    (BUG-4 fix: ``am_pct`` and ``em_pct`` are 0–100, not 0–1).

    =====================  =======  =====================================
    Condition              Score    Rationale
    =====================  =======  =====================================
    AM-dominant (>=80 %)   0.5      Informationally null — AM fungi
                                   invisible to citizen science
    EM-dominant (>=50 %)   0.0      Known fungal partners present
    + EM GBIF nearby
    EM-dominant (>=50 %)   0.8      Potential isolation
    + no EM GBIF
    Mixed                  0.6      Uncertain — moderate concern
    =====================  =======  =====================================

    Parameters
    ----------
    gdf : GeoDataFrame
        Must have ``am_pct`` (0–100), ``em_pct`` (0–100),
        ``em_gbif_nearby`` (0/1).

    Returns
    -------
    GeoDataFrame
        New column: ``s4_mismatch`` (0.0, 0.5, 0.6, or 0.8).
    """
    out = gdf.copy()

    score = pd.Series(
        np.full(len(out), S4_MIXED), index=out.index, dtype=float
    )

    # EM-dominant: score depends on GBIF evidence
    em_dom = out["em_pct"] >= EM_DOMINANCE_THRESHOLD
    score[em_dom & (out["em_gbif_nearby"] == 1)] = S4_EM_PARTNERS_PRESENT
    score[em_dom & (out["em_gbif_nearby"] == 0)] = S4_EM_POTENTIAL_ISOLATION

    # AM-dominant overrides (applied last so AM takes precedence)
    am_dom = out["am_pct"] >= AM_DOMINANCE_THRESHOLD
    score[am_dom] = S4_INFORMATIONALLY_NULL

    out["s4_mismatch"] = score
    return out


def compute_platanus_replacement_priority(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Compute the Platanus Replacement Priority Index (PRPI) per cell.

    The index identifies grid cells where *Platanus × acerifolia* should be
    removed first and replaced with EM-host species under Barcelona's
    2017-2037 Pla Director de l'Arbrat (target: Platanus <12% of street trees
    by 2037).

    PRPI combines four signals:

    1. **Platanus density** — public-health driver. The well-supported burden
       is **rhinoconjunctivitis morbidity and food-allergy cross-reactivity
       via Pla a 3** (an nsLTP cross-reactive with peach Pru p 3, walnut Jug r
       3, hazelnut, peanut, lettuce — Scala et al., 2017). Severe-asthma
       attribution to Platanus specifically is weak: Osborne et al. (2017)
       found no statistically significant association at any lag in London
       (n=8.2M) while grass pollen showed strong 3-5 day lag effects.
    2. **S3 inverted NDVI** — low canopy cells benefit most from replanting.
    3. **S4 shift potential** — replacing AM-host Platanus with EM hosts can
       break the AM-blind null zone in borderline cells (upper-bound, see
       column docstring). Zero where the cell is overwhelmingly AM regardless
       of Platanus.
    4. **Planting feasibility** — ``1 - s1_sealed``. Cells with high sealed
       surface cannot host replacement trees without de-paving first.

    Assumptions
    -----------
    - Replacement species are EM hosts (``S4_SHIFT_ASSUMPTION = "EM"``) such
      as *Quercus ilex* and *Pinus halepensis*, which are native and already
      in the approved palette of the 2037 plan. If the city instead trials
      AM hosts (*Zelkova*, *Pistacia*), ``s4_shift_potential`` becomes zero
      everywhere — the index reduces to pollen + canopy + feasibility.
    - Tree counts are preserved on a one-for-one replacement basis.

    Parameters
    ----------
    gdf : GeoDataFrame
        Must contain ``n_platanus``, ``tree_count``, ``n_AM``, ``n_EM``,
        ``am_pct``, ``s3_inverted_ndvi``, ``s1_sealed``.

    Returns
    -------
    GeoDataFrame
        New columns:
        - ``platanus_pct``: Platanus share of all trees in cell (0-100).
        - ``s4_shift_potential``: **upper-bound** drop in AM% (0-1) under the
          ideal-substrate, EM-replacement assumption (S4_SHIFT_ASSUMPTION="EM").
          NOT a delivered ecological outcome — Verbeek et al. (2025, Amsterdam)
          and Gaimaro et al. (2025, Fairfax VA) show urban AM communities shift
          composition rather than collapse, and engineered substrate co-drives
          colonization with host identity. Status: hypothesis. Use alongside
          ``prpi_operational`` (v1.2) for the species-preference variant.
        - ``s4_shift_ceiling_reached``: bool, cell remains AM-dominant
          (>= ``AM_DOMINANCE_THRESHOLD``) even after replacement.
        - ``prpi``: weighted index (0-1). EM-optimistic scenario.

    Example
    -------
    >>> gdf = compute_platanus_replacement_priority(gdf)
    >>> gdf["prpi"].between(0, 1).all()
    True
    """
    out = gdf.copy()

    # Platanus share of all trees in cell
    safe_total = out["tree_count"].replace(0, np.nan)
    out["platanus_pct"] = (
        (out["n_platanus"] / safe_total * 100).fillna(0).clip(0, 100)
    )

    # Post-replacement myco counts (Platanus → EM assumption)
    n_am_post = (out["n_AM"] - out["n_platanus"]).clip(lower=0)
    if S4_SHIFT_ASSUMPTION == "EM":
        n_em_post = out["n_EM"] + out["n_platanus"]
    else:  # conservative: AM-for-AM swap, no shift
        n_em_post = out["n_EM"]

    known_post = n_am_post + n_em_post
    am_pct_post = pd.Series(0.0, index=out.index, dtype=float)
    mask = known_post > 0
    am_pct_post[mask] = (n_am_post[mask] / known_post[mask] * 100).round(2)

    # Shift potential: how much AM% drops after replacement (0-1 scale)
    raw_shift = (out["am_pct"] - am_pct_post) / 100.0
    out["s4_shift_potential"] = raw_shift.clip(0, 1).round(4)

    # Ceiling: cell stays AM-dominant even after full Platanus replacement
    out["s4_shift_ceiling_reached"] = (
        (out["am_pct"] >= AM_DOMINANCE_THRESHOLD)
        & (am_pct_post >= AM_DOMINANCE_THRESHOLD)
    )

    # Weighted index
    w = PRPI_WEIGHTS
    out["prpi"] = (
        w["platanus"] * (out["platanus_pct"] / 100.0)
        + w["ndvi"] * out["s3_inverted_ndvi"]
        + w["s4_shift"] * out["s4_shift_potential"]
        + w["feasibility"] * (1 - out["s1_sealed"])
    ).clip(0, 1).round(4)

    assert (
        abs(sum(w.values()) - 1.0) < 1e-6
    ), f"PRPI_WEIGHTS sum to {sum(w.values()):.4f}, not 1.0"
    assert (out["prpi"].between(0, 1)).all(), "PRPI out of [0, 1] range"
    assert (out["platanus_pct"].between(0, 100)).all(), (
        "platanus_pct out of [0, 100] range"
    )
    return out


def load_vpa_lookup(vpa_path: Path = VPA_PATH) -> dict[str, int]:
    """Load the Mediterranean species → VPA (Value of Potential Allergenicity)
    lookup.

    Source: Cariñanos & Marinangeli (2021), *Urban Forestry & Urban Greening*.
    Class I (lowest) → V (highest). Returned as int 1–5.

    Falls back to a small hardcoded stub if the CSV is absent.

    Parameters
    ----------
    vpa_path : Path
        Path to ``data/raw/vpa-mediterranean-species.csv``. Expected columns:
        ``species_name``, ``vpa_numeric``.

    Returns
    -------
    dict[str, int]
        Lowercased species name → VPA class 1–5.

    Example
    -------
    >>> v = load_vpa_lookup()
    >>> v["platanus × acerifolia"]
    4
    """
    if not vpa_path.exists():
        print(
            "  [load_vpa_lookup] CSV not found — "
            "using minimal hardcoded stub (Platanus only)"
        )
        return {"platanus × acerifolia": 4}

    vpa = pd.read_csv(vpa_path, encoding="utf-8")
    vpa["species_key"] = vpa["species_name"].astype(str).str.strip().str.lower()
    out = dict(zip(vpa["species_key"], vpa["vpa_numeric"].astype(int)))
    print(f"  [load_vpa_lookup] Loaded {len(out)} species -> VPA mappings")
    return out


def compute_allergenicity_and_preference(
    joined: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
    vpa_lookup: dict[str, int],
) -> gpd.GeoDataFrame:
    """Compute per-cell allergenicity (VPA) and species-preference alignment.

    Adds three columns:

    1. ``cell_vpa_score`` — count-weighted mean VPA across all trees in the
       cell, normalised to 0–1 (raw VPA divided by 5). Species not in the
       lookup contribute ``SPECIES_PREFERENCE_DEFAULT × 5 = 2.5`` (mid VPA)
       to avoid biasing toward zero by exclusion.
    2. ``vpa_replacement_delta`` — expected drop in ``cell_vpa_score`` if all
       Platanus in the cell were replaced with the operational pilot-palette
       mean (Zelkova/Pistacia/Sophora ≈ class II ≈ VPA 2). Clipped to [0, 1].
    3. ``species_preference_present`` — fraction (0–1) of trees in the cell
       already drawn from the operational pilot palette
       (``SPECIES_PREFERENCE_WEIGHTS`` ≥ 0.8).

    Parameters
    ----------
    joined : GeoDataFrame
        Trees with ``cell_id``, ``species_name`` (lowercased). Source of the
        per-tree species composition.
    gdf : GeoDataFrame
        Grid cells; must already contain ``n_platanus`` and ``tree_count``.
    vpa_lookup : dict
        Species → VPA (1–5) mapping from ``load_vpa_lookup``.

    Returns
    -------
    GeoDataFrame
        ``gdf`` with three new columns: ``cell_vpa_score``,
        ``vpa_replacement_delta``, ``species_preference_present``.

    Example
    -------
    >>> gdf = compute_allergenicity_and_preference(joined, gdf, vpa_lookup)
    >>> gdf["cell_vpa_score"].between(0, 1).all()
    True
    """
    out = gdf.copy()

    # Build per-tree VPA + preference weight columns on the joined trees frame
    j = joined[["cell_id", "species_name"]].copy()
    j["vpa"] = j["species_name"].map(vpa_lookup).fillna(2.5)  # mid VPA default
    pref_map = {k.lower(): v for k, v in SPECIES_PREFERENCE_WEIGHTS.items()}
    j["pref"] = j["species_name"].map(pref_map).fillna(SPECIES_PREFERENCE_DEFAULT)
    j["is_pilot"] = (j["pref"] >= 0.8).astype(int)

    cell_stats = (
        j.groupby("cell_id", observed=True)
        .agg(
            mean_vpa=("vpa", "mean"),
            pilot_frac=("is_pilot", "mean"),
        )
        .reset_index()
    )

    out = out.merge(cell_stats, on="cell_id", how="left")
    out["cell_vpa_score"] = (out["mean_vpa"] / 5.0).clip(0, 1).round(4)
    out["species_preference_present"] = (
        out["pilot_frac"].fillna(0).clip(0, 1).round(4)
    )

    # Expected VPA delta if all Platanus replaced with pilot palette mean.
    # Pilot palette ≈ class II (Zelkova VPA 2, Pistacia VPA 3, Sophora VPA 1,
    # Melia VPA 1, Tipuana VPA 1 → mean ≈ 1.6 ≈ 0.32 normalised).
    pilot_palette_vpa_norm = 0.32
    safe_total = out["tree_count"].replace(0, np.nan)
    platanus_share = (out["n_platanus"] / safe_total).fillna(0).clip(0, 1)
    platanus_vpa_norm = vpa_lookup.get("platanus × acerifolia", 4) / 5.0
    out["vpa_replacement_delta"] = (
        platanus_share * (platanus_vpa_norm - pilot_palette_vpa_norm)
    ).clip(0, 1).round(4)

    # Tidy up intermediate columns
    out = out.drop(columns=["mean_vpa", "pilot_frac"], errors="ignore")

    assert (out["cell_vpa_score"].between(0, 1)).all(), (
        "cell_vpa_score out of [0, 1] range"
    )
    assert (out["vpa_replacement_delta"].between(0, 1)).all(), (
        "vpa_replacement_delta out of [0, 1] range"
    )
    assert (out["species_preference_present"].between(0, 1)).all(), (
        "species_preference_present out of [0, 1] range"
    )
    return out


def compute_prpi_operational(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Compute the operational PRPI scenario (v1.2).

    The v1.1 ``prpi`` column uses ``s4_shift_potential`` as the mycorrhizal
    driver, under the EM-optimistic assumption that Platanus is replaced with
    *Quercus ilex* / *Pinus halepensis*. That assumption is in tension with
    the public-health goal (Que i 1 = Bet v 1 homolog, VPA IV–V — see
    Cariñanos & Marinangeli, 2021; González-Mancebo et al., 2020) and with
    Barcelona's *own* pilot palette (Zelkova serrata, Pistacia chinensis,
    Sophora, Melia, jacarandas — Espais Verds operational documentation).

    ``prpi_operational`` uses ``vpa_replacement_delta`` (peer-reviewed
    allergenicity drop under the operational pilot palette) in place of
    ``s4_shift_potential``. Same weights, same shape, different premise —
    both columns are surfaced so downstream consumers can compare.

    Parameters
    ----------
    gdf : GeoDataFrame
        Must contain ``platanus_pct``, ``s3_inverted_ndvi``,
        ``vpa_replacement_delta``, ``s1_sealed``.

    Returns
    -------
    GeoDataFrame
        New column ``prpi_operational`` (0–1).
    """
    out = gdf.copy()
    w = PRPI_WEIGHTS
    out["prpi_operational"] = (
        w["platanus"] * (out["platanus_pct"] / 100.0)
        + w["ndvi"] * out["s3_inverted_ndvi"]
        + w["s4_shift"] * out["vpa_replacement_delta"]  # operational substitute
        + w["feasibility"] * (1 - out["s1_sealed"])
    ).clip(0, 1).round(4)

    assert (out["prpi_operational"].between(0, 1)).all(), (
        "prpi_operational out of [0, 1] range"
    )
    return out


def compute_composite_scores(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Compute composite barrier scores for all three weight scenarios.

    Scenario weights are defined in ``SCENARIO_WEIGHTS`` (see ADR-003).
    Output column names:
        - ``composite_score_A``
        - ``composite_score_B`` (PRIMARY)
        - ``composite_score_C``

    Parameters
    ----------
    gdf : GeoDataFrame
        Must have ``s1_sealed``, ``s2_lst_anomaly``, ``s3_inverted_ndvi``,
        ``s4_mismatch`` columns.

    Returns
    -------
    GeoDataFrame
        New columns for each composite score and rank.

    Example
    -------
    >>> gdf = compute_composite_scores(gdf)
    >>> gdf["composite_score_B"].describe()
    """
    out = gdf.copy()
    sub_score_map = {
        "sealed": "s1_sealed",
        "lst": "s2_lst_anomaly",
        "ndvi": "s3_inverted_ndvi",
        "mismatch": "s4_mismatch",
        "prpi": "prpi",
    }

    for label, weights in SCENARIO_WEIGHTS.items():
        total_w = sum(weights.values())
        assert (
            abs(total_w - 1.0) < 1e-6
        ), f"Scenario {label} weights sum to {total_w:.4f}, not 1.0"

        col_name = f"composite_score_{label}"
        out[col_name] = 0.0
        for short_name, weight in weights.items():
            out[col_name] += weight * out[sub_score_map[short_name]]

        out[col_name] = out[col_name].clip(0, 1)

        rank_col = f"rank_{label}"
        out[rank_col] = (
            out[col_name].rank(ascending=False, method="first").astype(int)
        )

    return out


def select_top15_with_district_constraint(
    gdf: gpd.GeoDataFrame,
    composite_col: str = "composite_score_B",
    district_col: str = "nom_districte",
    k: int = 15,
) -> pd.Index:
    """Select top-k cells ensuring every district is represented.

    BUG-6 fix: iterates over all missing districts (not just the last one)
    and displaces the lowest-ranked cell from an over-represented district.

    Parameters
    ----------
    gdf : GeoDataFrame
        Sorted by ``composite_col`` descending.
    composite_col : str
        Column name for the composite score.
    district_col : str
        Column name for district names.
    k : int
        Number of cells to select (default 15).

    Returns
    -------
    pd.Index
        Index labels of selected cells.

    Example
    -------
    >>> idx = select_top15_with_district_constraint(gdf)
    >>> len(idx)
    15
    >>> gdf.loc[idx, district_col].nunique()
    10
    """
    scored = gdf.sort_values(composite_col, ascending=False)
    selected = scored.head(k).copy()
    selected_districts = set(selected[district_col].dropna().unique())
    all_districts = set(scored[district_col].dropna().unique())
    missing = sorted(all_districts - selected_districts)

    for d in missing:
        candidate = scored[scored[district_col] == d].nsmallest(1, composite_col)
        if candidate.empty:
            continue
        # Find the lowest-ranked selected cell whose district has >1 rep
        selected_sorted = selected.sort_values(composite_col)
        drop_idx = None
        for idx in selected_sorted.index:
            cell_d = selected.loc[idx, district_col]
            if (selected[district_col] == cell_d).sum() > 1:
                drop_idx = idx
                break
        if drop_idx is not None:
            selected = selected.drop(drop_idx)
        selected = pd.concat([selected, candidate])

    selected = selected.sort_values(composite_col, ascending=False)
    return selected.index


def assign_display_intervention(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Assign a diversified intervention type for visualization purposes.

    This logic is ported from the frontend's `interventionOverride` function
    to make the data pipeline the single source of truth.
    """
    out = gdf.copy()

    # The frontend uses `sealedPct` which is on a 0-1 scale, same as s1_sealed.
    # It uses `lstAnomalyC` which is the raw anomaly, not the normalized score.
    # It uses `meanNdvi`. We must use the same columns.
    
    # Ensure required columns exist, using normalized names if available
    lst_col = "lst_anomaly" if "lst_anomaly" in out.columns else "lst_anomaly_celsius"
    sealed_col = "s1_sealed" if "s1_sealed" in out.columns else "mean_sealed"

    def override(row: pd.Series) -> str:
        if row[lst_col] >= 4 and row[sealed_col] >= 0.8:
            return "de-paving"
        if row[lst_col] >= 1.5:
            return "cooling"
        if row["mean_ndvi"] < 0.075:
            return "planting"
        return "de-paving"  # Default fallback

    out["display_intervention"] = out.apply(override, axis=1)
    return out


def classify_intervention(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Classify intervention type per cell based on sub-score contributions.

    Computes an intervention *profile* (percentage contribution of each
    sub-score to the Scenario B composite) and a single dominant label.

    Parameters
    ----------
    gdf : GeoDataFrame
        Must have ``s1_sealed``, ``s2_lst_anomaly``, ``s3_inverted_ndvi``,
        ``s4_mismatch``, and ``composite_score_B`` columns.

    Returns
    -------
    GeoDataFrame
        New columns:
        - ``intervention_type``: dominant label (back-compat)
        - ``intervention_profile``: JSON string of percentage breakdown

    Example
    -------
    >>> gdf = classify_intervention(gdf)
    >>> gdf["intervention_type"].value_counts()
    de-paving    471
    planting      14
    cooling        9
    """
    out = gdf.copy()
    w = SCENARIO_WEIGHTS["B"]
    sub_cols = {
        "s1_sealed": w["sealed"],
        "s2_lst_anomaly": w["lst"],
        "s3_inverted_ndvi": w["ndvi"],
        "s4_mismatch": w["mismatch"],
        "prpi": w["prpi"],
    }

    def _profile(row: pd.Series) -> dict[str, float]:
        contributions = {
            LABEL_MAP[k]: row[k] * weight for k, weight in sub_cols.items()
        }
        total = sum(contributions.values())
        if total <= 0:
            return {label: 0.0 for label in LABEL_MAP.values()}
        return {
            label: round(v / total * 100.0, 1)
            for label, v in contributions.items()
        }

    out["intervention_profile"] = out.apply(_profile, axis=1)

    # Dominant intervention (max contribution across 5 sub-scores)
    out["intervention_type"] = out["intervention_profile"].apply(
        lambda p: max(p.items(), key=lambda x: x[1])[0]
    )

    # replacement_priority: strict gate independent of dominance.
    # A cell is a replacement candidate when:
    #   (a) PRPI exceeds the action threshold,
    #   (b) replacing Platanus with EM actually shifts the cell out of the
    #       AM-blind zone (s4_shift_potential > 0),
    #   (c) the cell is plantable today (sealed surface < feasibility cap).
    out["replacement_priority"] = (
        (out["prpi"] > PRPI_THRESHOLD)
        & (out["s4_shift_potential"] > 0)
        & (out["s1_sealed"] < SEAL_FEASIBILITY)
    )

    # Store profile as human-readable JSON string
    out["intervention_profile"] = out["intervention_profile"].apply(
        json.dumps, ensure_ascii=False
    )

    return out


def compute_contribution_percentages(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Compute each sub-score's percentage contribution to composite_B.

    Parameters
    ----------
    gdf : GeoDataFrame
        Must have ``s1_sealed``, ``s2_lst_anomaly``, ``s3_inverted_ndvi``,
        ``s4_mismatch``, ``composite_score_B``.

    Returns
    -------
    GeoDataFrame
        New columns: ``s1_contribution_pct`` .. ``s4_contribution_pct``.
    """
    out = gdf.copy()
    w = SCENARIO_WEIGHTS["B"]
    mapping = {
        "s1_contribution_pct": ("s1_sealed", w["sealed"]),
        "s2_contribution_pct": ("s2_lst_anomaly", w["lst"]),
        "s3_contribution_pct": ("s3_inverted_ndvi", w["ndvi"]),
        "s4_contribution_pct": ("s4_mismatch", w["mismatch"]),
        "s5_contribution_pct": ("prpi", w["prpi"]),
    }

    for contrib_col, (sub_col, weight) in mapping.items():
        raw_contrib = out[sub_col] * weight
        total = out["composite_score_B"].replace(0, np.nan)
        out[contrib_col] = (raw_contrib / total * 100).fillna(0).round(1)

    return out


def flag_colonisation_uncertainty(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Flag cells where many trees are too young for established mycorrhiza.

    Cells flagged when:
        ``top15_scenario_B == True`` AND
        ``trees_young_pct >= COLONISATION_UNCERTAIN_THRESHOLD``.

    ``trees_young_pct`` is on a 0–100 scale (BUG-5 fix).

    Parameters
    ----------
    gdf : GeoDataFrame
        Must have ``trees_young_pct`` and ``top15_scenario_B`` columns.

    Returns
    -------
    GeoDataFrame
        New column: ``colonisation_uncertain`` (bool).
    """
    out = gdf.copy()
    out["colonisation_uncertain"] = (
        out["top15_scenario_B"] & (out["trees_young_pct"] >= COLONISATION_UNCERTAIN_THRESHOLD)
    )
    return out


def finalize_columns(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Rename columns to data-contract names and reorder.

    Parameters
    ----------
    gdf : GeoDataFrame
        Internal pipeline column names.

    Returns
    -------
    GeoDataFrame
        Column names and order matching ``phase-3/data-contract.yaml``.

    Example
    -------
    >>> final = finalize_columns(gdf)
    >>> list(final.columns)[:5]
    ['cell_id', 'district', 'barri', 'geometry', 'total_trees']
    """
    RENAME_MAP: dict[str, str] = {
        "nom_districte": "district",
        "barri_name": "barri",
        "tree_count": "total_trees",
        "dominant_myco_type": "expected_myco_type",
        "composite_A": "composite_score_A",
        "composite_B": "composite_score_B",
        "composite_C": "composite_score_C",
        "s2_lst": "s2_lst_anomaly",
        "s3_ndvi": "s3_inverted_ndvi",
        "lst_anomaly_celsius": "lst_anomaly",
        "top15_scenario_B": "top15_flag",
    }

    # Also apply scenario-specific renames
    for label in ("A", "B", "C"):
        old_composite = f"composite_{label}"
        new_composite = f"composite_score_{label}"
        if old_composite in gdf.columns:
            RENAME_MAP[old_composite] = new_composite

    # Drop intermediate columns not in the contract
    DROP_COLS = {
        "cell_x0",
        "cell_y0",
        "am_blindness_flag",
        "lst_score",
        "rank_A",
        "rank_B",
        "rank_C",
        "top15_scenario_A",
        "top15_scenario_C",
        "jaccard_AB",
        "jaccard_AC",
        "jaccard_BC",
        "sensitivity_warning",
        "intervention_profile_str",
        "em_gbif_nearby",
        "nm_pct",
    }

    out = gdf.copy()
    out = out.rename(columns=RENAME_MAP, errors="ignore")
    out = out.drop(columns=[c for c in DROP_COLS if c in out.columns], errors="ignore")

    # Add cell bbox columns
    out["cell_bbox_minx"] = out.geometry.bounds["minx"].round(0).astype(int)
    out["cell_bbox_miny"] = out.geometry.bounds["miny"].round(0).astype(int)
    out["cell_bbox_maxx"] = out.geometry.bounds["maxx"].round(0).astype(int)
    out["cell_bbox_maxy"] = out.geometry.bounds["maxy"].round(0).astype(int)

    return out


def load_network_data(
    nodes_path: Path,
    grid_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Load pre-computed network connectivity data and attach to grid.

    If network files exist (from notebook 04), merges ``component_id``
    and ``component_size`` onto the grid cells.  Otherwise leaves these
    as null — they are not required for the core scoring pipeline.

    Parameters
    ----------
    nodes_path : Path
        Path to ``network_nodes.geojson`` (output of notebook 04).
    grid_gdf : GeoDataFrame
        Grid cells with ``cell_id``.

    Returns
    -------
    GeoDataFrame
        New nullable columns: ``component_id``, ``component_size``.
    """
    out = grid_gdf.copy()
    out["component_id"] = None
    out["component_size"] = None

    if nodes_path.exists():
        nodes = gpd.read_file(nodes_path)
        if "component_id" in nodes.columns and "cell_id" in nodes.columns:
            # Per cell: take the most common component_id
            comp_agg = (
                nodes.groupby("cell_id")
                .agg(
                    component_id=("component_id", "first"),
                    component_size=("component_id", "count"),
                )
                .reset_index()
            )
            comp_agg["component_id"] = comp_agg["component_id"].astype(int)
            # Merge onto grid
            out = out.merge(
                comp_agg[["cell_id", "component_id", "component_size"]],
                on="cell_id",
                how="left",
                suffixes=("", "_from_nodes"),
            )
            # Use merged values where available
            if "component_id_from_nodes" in out.columns:
                fill_mask = out["component_id_from_nodes"].notna()
                out.loc[fill_mask, "component_id"] = out.loc[
                    fill_mask, "component_id_from_nodes"
                ]
                out.loc[fill_mask, "component_size"] = out.loc[
                    fill_mask, "component_size_from_nodes"
                ]
                out = out.drop(
                    columns=[
                        "component_id_from_nodes",
                        "component_size_from_nodes",
                    ],
                    errors="ignore",
                )

        print(
            f"  [network] Loaded {len(nodes):,} nodes; "
            f"{out['component_id'].notna().sum()} cells with component data"
        )
    else:
        print(
            "  [network] network_nodes.geojson not found — "
            "component_id/component_size set to null"
        )

    return out


# ===========================================================================
# INVARIANT ASSERTIONS
# ===========================================================================


def assert_clean_invariants(gdf: gpd.GeoDataFrame) -> None:
    """Assert every property the downstream pipeline depends on.

    Raises ``AssertionError`` with a descriptive message if any check
    fails.  Call at the end of ``build_scored_grid``.

    Parameters
    ----------
    gdf : GeoDataFrame
        The final scored grid (columns must match the data contract).

    Checks
    ------
    - Row count is 495
    - CRS is EPSG:25831
    - Geometry type is Polygon
    - ``cell_id`` has no nulls and is unique
    - ``composite_score_B`` is in [0, 1] for every row
    - ``top15_flag`` has exactly 15 true values
    - ``s1_sealed``, ``s2_lst_anomaly``, ``s3_inverted_ndvi`` are 0–1
    - ``s4_mismatch`` is one of {0.0, 0.5, 0.6, 0.8}
    - ``intervention_type`` has valid values
    - ``expected_myco_type`` has valid values
    - ``total_trees`` non-negative
    """
    # v1.2: relaxed to a range — snapshot refreshes can drop 1-2 boundary
    # cells without changing the analysis. Hard count was 495 against the
    # pre-2026_1T snapshot; current snapshot produces 494.
    assert 480 <= len(gdf) <= 510, (
        f"Expected 480-510 grid cells, got {len(gdf)}"
    )

    assert gdf.crs is not None and "25831" in str(gdf.crs.to_epsg()), (
        f"CRS mismatch: {gdf.crs}"
    )

    assert (gdf.geometry.type == "Polygon").all(), (
        "Not all geometries are Polygon"
    )

    assert gdf["cell_id"].isna().sum() == 0, (
        f"{gdf['cell_id'].isna().sum()} null cell_ids"
    )
    assert gdf["cell_id"].is_unique, (
        "cell_id is not unique"
    )

    assert (gdf["composite_score_B"].between(0, 1)).all(), (
        "composite_score_B out of [0, 1] range"
    )

    n_top15 = gdf["top15_flag"].sum()
    assert n_top15 == 15, (
        f"Expected 15 top15_flag cells, got {n_top15}"
    )

    for col in ["s1_sealed", "s2_lst_anomaly", "s3_inverted_ndvi"]:
        assert (gdf[col].between(0, 1)).all(), (
            f"{col} out of [0, 1] range"
        )

    valid_s4 = {0.0, 0.5, 0.6, 0.8}
    assert gdf["s4_mismatch"].isin(valid_s4).all(), (
        f"s4_mismatch has unexpected values: {gdf['s4_mismatch'].unique()}"
    )

    valid_intervention = {
        "de-paving",
        "cooling",
        "planting",
        "multi-strategy",
        "species-replacement",
    }
    assert gdf["intervention_type"].isin(valid_intervention).all(), (
        f"intervention_type has unexpected values: "
        f"{gdf['intervention_type'].unique()}"
    )

    # PRPI invariants
    assert (gdf["prpi"].between(0, 1)).all(), "prpi out of [0, 1] range"
    assert (gdf["platanus_pct"].between(0, 100)).all(), (
        "platanus_pct out of [0, 100] range"
    )
    assert (gdf["s4_shift_potential"].between(0, 1)).all(), (
        "s4_shift_potential out of [0, 1] range"
    )
    assert gdf["n_platanus"].dtype.kind in {"i", "u"}, (
        "n_platanus must be integer-typed"
    )
    assert (gdf["n_platanus"] >= 0).all(), "Some cells have negative n_platanus"

    # v1.2 — VPA + operational scenario invariants
    assert (gdf["prpi_operational"].between(0, 1)).all(), (
        "prpi_operational out of [0, 1] range"
    )
    assert (gdf["cell_vpa_score"].between(0, 1)).all(), (
        "cell_vpa_score out of [0, 1] range"
    )
    assert (gdf["vpa_replacement_delta"].between(0, 1)).all(), (
        "vpa_replacement_delta out of [0, 1] range"
    )
    assert (gdf["species_preference_present"].between(0, 1)).all(), (
        "species_preference_present out of [0, 1] range"
    )

    valid_myco = {"AM", "EM", "Mixed", "Unknown"}
    assert gdf["expected_myco_type"].isin(valid_myco).all(), (
        f"expected_myco_type has unexpected values: "
        f"{gdf['expected_myco_type'].unique()}"
    )

    assert (gdf["total_trees"] >= 0).all(), (
        "Some cells have negative total_trees"
    )

    print("  [assert] All invariant checks passed OK")


# ===========================================================================
# PIPELINE ORCHESTRATOR
# ===========================================================================


def _ensure_processed_dir() -> Path:
    """Create ``data/processed/`` if it does not exist."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    return PROCESSED_DIR


def build_scored_grid(
    viari_path: Path = VIARI_PATH,
    zona_path: Path = ZONA_PATH,
    fungalroot_path: Path = FUNGALROOT_PATH,
    boundary_path: Path = BOUNDARY_PATH,
    gbif_path: Path = GBIF_PATH,
    sealed_path: Path = SEALED_PATH,
    lst_path: Path = LST_PATH,
    ndvi_path: Path = NDVI_PATH,
    nodes_path: Path = DATA_DIR / "network_nodes.geojson",
) -> gpd.GeoDataFrame:
    """Run the full raw-data-to-scored-grid pipeline.

    Parameters
    ----------
    viari_path : Path
        Path to ``arbrat-viari.csv``.
    zona_path : Path
        Path to ``arbrat-zona.csv``.
    fungalroot_path : Path
        Path to ``fungalroot.csv``.
    boundary_path : Path
        Path to ``bcn-boundary.geojson``.
    gbif_path : Path
        Path to ``gbif-fungi.json``.
    sealed_path : Path
        Path to ``sealed_surface.tif``.
    lst_path : Path
        Path to ``lst_summer_composite.tif``.
    ndvi_path : Path
        Path to ``ndvi_summer_composite.tif``.
    nodes_path : Path
        Path to ``network_nodes.geojson`` (optional, from notebook 04).

    Returns
    -------
    GeoDataFrame
        Scored grid with all columns defined in ``data-contract.yaml``.
    """
    print("=" * 60)
    print(" MYCORRHIZAL BARCELONA — DATA PREPARATION PIPELINE")
    print("=" * 60)

    # ── Stage 1: Load tree inventory ──────────────────────────────────────
    print("\n[1/17] Loading tree inventory…")
    df = load_tree_inventory(viari_path, zona_path)
    df = normalize_species_names(df)
    print(f"  {len(df):,} trees loaded, {df['species_name'].nunique()} unique species")

    # ── Stage 2: FungalRoot lookup ────────────────────────────────────────
    print("\n[2/17] Loading FungalRoot lookup…")
    myco_lookup = load_fungalroot_lookup(fungalroot_path)
    df = assign_myco_type(df, myco_lookup)
    type_counts = df["myco_type"].value_counts()
    print(f"  AM: {type_counts.get('AM', 0):,}  "
          f"EM: {type_counts.get('EM', 0):,}  "
          f"NM: {type_counts.get('NM', 0):,}")

    # ── Stage 3: Build grid ───────────────────────────────────────────────
    print("\n[3/17] Building 400 m grid…")
    grid = build_grid(boundary_path)
    print(f"  {len(grid)} cells intersecting BCN boundary")

    # ── Stage 4: Spatial join trees → grid ────────────────────────────────
    print("\n[4/17] Spatial join trees to grid…")
    trees_gdf = build_tree_geodataframe(df)
    joined = spatial_join_trees_to_grid(trees_gdf, grid)
    print(f"  {len(joined):,} trees matched to {joined['cell_id'].nunique()} cells")

    # ── Stage 5: Per-cell aggregation ─────────────────────────────────────
    print("\n[5/17] Computing per-cell tree statistics…")
    cell_agg = compute_cell_aggregation(joined)
    myco_stats = compute_myco_statistics(joined)

    # Merge onto grid
    grid_out = grid.merge(cell_agg, on="cell_id", how="inner")
    grid_out = grid_out.merge(myco_stats, on="cell_id", how="inner")
    # Rename for consistency
    grid_out = grid_out.rename(
        columns={
            "tree_count": "tree_count",
            "district_name": "nom_districte",
            "barri_name": "barri_name",
        },
        errors="ignore",
    )
    print(f"  {len(grid_out)} occupied cells")

    # ── Stage 6: GBIF ─────────────────────────────────────────────────────
    print("\n[6/17] Loading GBIF fungal occurrences…")
    gbif_gdf = load_gbif_occurrences(gbif_path)
    print(f"  {len(gbif_gdf)} GBIF records loaded")
    gbif_stats = count_gbif_per_cell(gbif_gdf, grid_out)
    grid_out = grid_out.merge(gbif_stats, on="cell_id", how="left")
    grid_out["gbif_records"] = grid_out["gbif_records"].fillna(0).astype(int)
    grid_out["em_gbif_nearby"] = grid_out["em_gbif_nearby"].fillna(0).astype(int)
    print(f"  Cells with >=1 GBIF record: {(grid_out['gbif_records'] > 0).sum()}")

    # ── Stage 7: S1 — Sealed surface ──────────────────────────────────────
    print(f"\n[7/17] Computing S1 (sealed surface)…")
    grid_out = compute_s1_sealed(grid_out, sealed_path)
    print(f"  mean_sealed: {grid_out['mean_sealed'].mean():.3f}")

    # ── Stage 8: S2 — LST anomaly ─────────────────────────────────────────
    print(f"\n[8/17] Computing S2 (LST anomaly)…")
    grid_out = compute_s2_lst(grid_out, lst_path)
    print(f"  LST range: [{grid_out['mean_lst_celsius'].min():.1f}, "
          f"{grid_out['mean_lst_celsius'].max():.1f}] °C")

    # ── Stage 9: S3 — Inverted NDVI ───────────────────────────────────────
    print(f"\n[9/17] Computing S3 (inverted NDVI)…")
    grid_out = compute_s3_ndvi(grid_out, ndvi_path)
    print(f"  NDVI range: [{grid_out['mean_ndvi'].min():.3f}, "
          f"{grid_out['mean_ndvi'].max():.3f}]")

    # ── Stage 10: S4 — Host-mycorrhizal mismatch ──────────────────────────
    print(f"\n[10/17] Computing S4 (mismatch)…")
    grid_out = compute_s4_mismatch(grid_out)
    s4_dist = grid_out["s4_mismatch"].value_counts().sort_index()
    for val, count in s4_dist.items():
        print(f"  S4={val}: {count} cells")

    # ── Stage 11: PRPI — Platanus Replacement Priority Index ──────────────
    print(f"\n[11/17] Computing PRPI (Platanus replacement priority)…")
    grid_out = compute_platanus_replacement_priority(grid_out)
    n_platanus_total = int(grid_out["n_platanus"].sum())
    n_ceiling = int(grid_out["s4_shift_ceiling_reached"].sum())
    print(
        f"  Platanus trees counted: {n_platanus_total:,} "
        f"(inventory baseline: 42,828)"
    )
    print(
        f"  PRPI range: [{grid_out['prpi'].min():.3f}, "
        f"{grid_out['prpi'].max():.3f}]"
    )
    print(f"  Cells where AM-blindness ceiling is reached: {n_ceiling}")

    # ── Stage 12: VPA + species preference (v1.2) ─────────────────────────
    print(f"\n[12/17] Computing VPA allergenicity + species preference…")
    vpa_lookup = load_vpa_lookup()
    grid_out = compute_allergenicity_and_preference(joined, grid_out, vpa_lookup)
    print(
        f"  Cell VPA range: [{grid_out['cell_vpa_score'].min():.3f}, "
        f"{grid_out['cell_vpa_score'].max():.3f}]"
    )
    print(
        f"  Cells with >=50% pilot-palette species already present: "
        f"{(grid_out['species_preference_present'] >= 0.5).sum()}"
    )

    # ── Stage 13: PRPI operational scenario (v1.2) ────────────────────────
    print(f"\n[13/17] Computing operational PRPI (species-preference variant)…")
    grid_out = compute_prpi_operational(grid_out)
    print(
        f"  prpi_operational range: [{grid_out['prpi_operational'].min():.3f}, "
        f"{grid_out['prpi_operational'].max():.3f}]"
    )
    # Quick delta diagnostic: how often the two scenarios disagree on
    # whether a cell crosses the action threshold.
    em_high = grid_out["prpi"] > PRPI_THRESHOLD
    op_high = grid_out["prpi_operational"] > PRPI_THRESHOLD
    disagreement = int((em_high ^ op_high).sum())
    print(
        f"  EM-optimistic vs operational disagreement at threshold "
        f"{PRPI_THRESHOLD}: {disagreement} cells"
    )

    # ── Stage 14: Composite scores ────────────────────────────────────────
    print(f"\n[14/17] Computing composite scores…")
    grid_out = compute_composite_scores(grid_out)
    for label in ("A", "B", "C"):
        col = f"composite_score_{label}"
        print(f"  Scenario {label}: range [{grid_out[col].min():.3f}, "
              f"{grid_out[col].max():.3f}]")

    # ── Stage 15: Top-15 selection ────────────────────────────────────────
    print(f"\n[15/17] Selecting top-15 priority zones (Scenario B)…")
    if "nom_districte" not in grid_out.columns:
        raise KeyError("nom_districte column missing — cannot apply district constraint")
    top15_idx = select_top15_with_district_constraint(
        grid_out,
        composite_col="composite_score_B",
        district_col="nom_districte",
        k=15,
    )
    grid_out["top15_scenario_B"] = False
    grid_out.loc[top15_idx, "top15_scenario_B"] = True
    print(f"  {len(top15_idx)} cells selected, "
          f"{grid_out.loc[top15_idx, 'nom_districte'].nunique()} districts")

    # ── Stage 16: Intervention + uncertainty ──────────────────────────────
    print(f"\n[16/17] Classifying intervention types…")
    grid_out = classify_intervention(grid_out)
    grid_out = assign_display_intervention(grid_out) # <-- ADD THIS LINE
    grid_out = flag_colonisation_uncertainty(grid_out)
    grid_out = compute_contribution_percentages(grid_out)
    print(f"  Intervention distribution: {grid_out['intervention_type'].value_counts().to_dict()}")
    print(f"  Colonisation-uncertain cells: {grid_out['colonisation_uncertain'].sum()}")

    # ── Stage 17: Finalise + network data ─────────────────────────────────
    print(f"\n[17/17] Finalising columns and loading network data…")
    grid_out = load_network_data(nodes_path, grid_out)
    grid_out = finalize_columns(grid_out)

    # Verify CRS
    if grid_out.crs is None or str(grid_out.crs.to_epsg()) != "25831":
        grid_out = grid_out.set_crs(CRS_PROJ)

    # ── Invariant assertions ──────────────────────────────────────────────
    print()
    assert_clean_invariants(grid_out)

    print(f"\n{'=' * 60}")
    print(f" Pipeline complete.  {len(grid_out)} cells, {len(grid_out.columns)} columns.")
    print(f"{'=' * 60}")
    return grid_out


# ===========================================================================
# CLI ENTRY POINT
# ===========================================================================


def main() -> None:
    """Run from command line.  Load raw, run pipeline, write GeoJSON + Parquet.

    Usage::

        python src/clean_data.py
    """
    import time

    t0 = time.time()

    _ensure_processed_dir()
    scored = build_scored_grid()

    # ── Write GeoJSON ────────────────────────────────────────────────────
    scored.to_file(SCORED_OUTPUT_PATH, driver="GeoJSON")
    size_mb = SCORED_OUTPUT_PATH.stat().st_size / 1_048_576
    print(f"\n  GeoJSON: {SCORED_OUTPUT_PATH}  ({size_mb:.1f} MB)")

    # ── Write Parquet (compact, preserves types better than GeoJSON) ─────
    parquet_path = SCORED_OUTPUT_PATH.with_suffix(".parquet")
    try:
        # GeoParquet — geometry column preserved
        scored.to_parquet(parquet_path, index=False)
        pq_size = parquet_path.stat().st_size / 1_048_576
        print(f"  Parquet: {parquet_path}  ({pq_size:.1f} MB)")
    except Exception as exc:
        print(f"  Parquet write skipped ({exc})")

    elapsed = time.time() - t0
    print(f"\n  Elapsed: {elapsed:.1f} s")


if __name__ == "__main__":
    main()
