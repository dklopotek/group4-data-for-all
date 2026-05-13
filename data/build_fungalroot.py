"""
build_fungalroot.py — downloads FungalRoot v2.0 from GBIF and saves
data/fungalroot.csv (species_name, myco_type).

Run: python data/build_fungalroot.py
"""
import csv, io, requests, zipfile
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent
DEST     = DATA_DIR / "fungalroot.csv"
URL      = "https://orphans.gbif.org/EE/744edc21-8dd2-474e-8a0b-b8c3d56a3c2d.232.zip"

BCN_CHECK = ["Platanus", "Pinus", "Quercus", "Celtis", "Melia", "Tipuana"]

def main():
    if DEST.exists() and DEST.stat().st_size > 10_000:
        print(f"[skip] fungalroot.csv already exists ({DEST.stat().st_size // 1024} KB)")
        return

    print("Downloading FungalRoot v2.0 from GBIF ...")
    r = requests.get(URL, timeout=180)
    r.raise_for_status()
    print(f"  Downloaded {len(r.content) // 1024} KB")

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        occ_raw  = z.read("occurrences.csv").decode("utf-8")
        meas_raw = z.read("measurements.csv").decode("utf-8")

    # Occurrences: get occurrenceID (int) + scientificName
    occ = pd.read_csv(io.StringIO(occ_raw), sep=",", low_memory=False,
                      usecols=["occurrenceID", "scientificName"])
    occ["occurrenceID"] = occ["occurrenceID"].astype(str).str.strip()
    occ["species_name"] = (occ["scientificName"].str.strip()
                           .str.extract(r"^([A-Z][a-z\-]+ [a-z\-x]+)"))

    # Measurements: Core ID = OBS<number> — strip prefix to join
    rows = []
    for row in csv.reader(io.StringIO(meas_raw)):
        if len(row) >= 3:
            rows.append(row[:3])
    meas = pd.DataFrame(rows[1:], columns=["core_id", "measurementType", "measurementValue"])
    meas["core_id"] = meas["core_id"].str.replace("^OBS", "", regex=True).str.strip()

    myco = (meas[meas["measurementType"] == "Mycorrhiza type"]
            [["core_id", "measurementValue"]].copy())
    myco.columns = ["occurrenceID", "myco_type"]

    merged = occ.merge(myco, on="occurrenceID", how="inner")
    merged = merged.dropna(subset=["species_name", "myco_type"])

    # Per species: most commonly recorded type wins
    result = (merged.groupby("species_name")["myco_type"]
              .agg(lambda x: x.value_counts().index[0])
              .reset_index())
    result.columns = ["species_name", "myco_type"]

    result.to_csv(DEST, index=False, encoding="utf-8")
    print(f"\nfungalroot.csv: {len(result):,} species")
    print(result["myco_type"].value_counts().to_string())

    print("\nKey Barcelona species check:")
    for genus in BCN_CHECK:
        match = result[result["species_name"].str.startswith(genus)]
        if len(match):
            sample = match.head(2)[["species_name", "myco_type"]].to_string(index=False)
            print(f"  {sample}")
        else:
            print(f"  {genus}: NOT FOUND")

if __name__ == "__main__":
    main()
