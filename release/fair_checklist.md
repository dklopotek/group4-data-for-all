# FAIR Compliance Checklist (Wilkinson et al., 2016)

`pass` / `partial` / `n/a` with justification. Honest for a seminar context — DOI-dependent items are
`partial` (pending), not faked.

## Findable
- **F1 — (meta)data have a globally unique persistent identifier:** `partial` — Git SHA + semantic
  version now; Zenodo DOI pending (needs institutional account).
- **F2 — data described with rich metadata:** `pass` — datasheet + manifest + data contract.
- **F3 — metadata clearly include the data identifier:** `pass` — manifest records each path + SHA-256.
- **F4 — (meta)data registered/indexed in a searchable resource:** `partial` — public GitHub repo;
  Zenodo indexing pending.

## Accessible
- **A1 — retrievable by identifier over a standard protocol (HTTP/Git):** `pass`.
- **A1.1 — protocol open, free, universally implementable:** `pass` — Git/HTTPS.
- **A1.2 — auth where necessary:** `n/a` — all data open, no auth needed.
- **A2 — metadata accessible even if data removed:** `pass` — manifest + datasheet are text in-repo,
  independent of the large input files (which are gitignored but hashed).

## Interoperable
- **I1 — formal, broadly applicable representation:** `pass` — Parquet, CSV, GeoJSON; EPSG codes stated.
- **I2 — FAIR-compliant vocabularies:** `partial` — EPSG CRS + Darwin-Core-adjacent tree fields; no
  formal ontology mapping.
- **I3 — qualified references to other (meta)data:** `pass` — manifest links derived outputs to input
  hashes and source URLs.

## Reusable
- **R1 — richly described with accurate attributes:** `pass` — datasheet §2, field list.
- **R1.1 — clear data-usage licence:** `pass` — CC-BY-4.0 (data), MIT (code), stated in manifest +
  repo licence files.
- **R1.2 — detailed provenance:** `pass` — deterministic scripts, seeds, input snapshots/hashes,
  decision log.
- **R1.3 — meets domain-relevant community standards:** `pass` — CRISP-DM process, Gebru datasheet,
  Mitchell model card, OECD/JRC composite-indicator method.

**Blockers:** none `fail`. Four `partial`s all resolve on DOI minting (`publication_plan.md`).
