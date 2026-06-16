# Evaluation Rigor Checklist — WORKED THROUGH (Group 4, 2026-06-09)

> Working reference, completed against this project's evidence before writing the verdict.
> Each box is checked only where the evidence backs it; `[~]` = partial/open, with the reason.
> Dual track: A = the killed mycorrhizal model (Cycle A), B = the allergen product (Cycle B).

---

## The bar

An honest verdict reports: (1) against the brief, (2) where it fails, (3) compared to what, plus
a stated confidence. All four are in `docs/evaluation-report.md` §2, §4, §3, §5 — for **both**
cycles.

---

## Back to the brief (both tracks)

- [x] **Found the S1 success criteria.** Two briefs: Cycle A `docs/problem-brief.md`; Cycle B
      `phase-6/phase-1-audit.md §B` (6 numeric criteria). Cycle A's structural criteria were
      noted as not load-bearing — the scientific claim is what we grade.
- [x] **Named the decision and who acts.** Espais Verds capital-planning analyst sequences the
      plane reduction.
- [x] **Finished "so the decision-maker should…"** — *…remove planes first in high source×exposure
      cells (e.g. Nou Barris over a denser-but-emptier Sant Martí cell).*
- [x] **Graded against the bar, not against "impressive."** Cycle A passed Phase 4 (impressive)
      and still failed Phase 5 — we graded validity, not polish.

---

## Track A — model checks

- [x] **Test set still sacred** — the frozen cluster was computed once; the kill used an
      *external* GBIF target, not a re-tune.
- [x] **Per-segment error done** — per-district residuals (NB Cell A2), not just aggregate.
- [x] **Worst segment named + mechanism** — Sarrià outlier cell (resid 0.334); and the systematic
      one: drop `mean_sealed` → 11× MAE (model = sealed re-skin).
- [x] **Stress tests run** — all 10 features dropped (NB Cell A3); no crash; the ecological
      features are inert (Δ≈0).
- [x] **Confidence reported** — cross-split spread (R² 0.9997 / 0.9991 / 0.877), 6× MAE gap,
      noise/seed stability. *(Linear model → no tree interval; reported the spatial-generalization
      spread instead, which is the honest uncertainty here.)*
- [x] **Five+ failure-gallery entries** — `docs/failure-gallery.md`: 6 cases (systematic +
      spectacular) + a 10-row stress table.

## Track B — conclusions checks

- [x] **Claim is one falsifiable sentence** — see `docs/validity-audit.md` / conclusions-brief.
- [x] **Exact evidence named** — `allergen_layers.parquet`, tests T1–T4, the specific numbers.
- [x] **All four threats addressed** — confounding (corr 0.30), selection (declared residents-only),
      spurious (pre-registered), cherry-picking (rejected layers reported). `docs/validity-audit.md`.
- [x] **Robustness done** — T4 3/3 perturbations; equity sensitivity 0.875 / 0.5.
- [x] **Reported the cuts that did NOT support a layer** — age (0.999 redundant), sex (no spatial
      signal), bike (no data) — all rejected in writing.
- [x] **Causal language audited** — the product claims *exposure*, never *causes*; no causal design,
      no causal words.

---

## The "compared to what" check (both tracks)

- [x] **Named the alternative** — Cycle A vs 3 baselines + the abiotic null; Cycle B vs the city's
      density-only rule.
- [x] **Reported the comparison, not the headline** — "0.877 vs −0.29 yet Δ −0.0195, p 0.989";
      "margin +0.046 over density-only".
- [x] **Weighed effort vs value** — Cycle A high effort/zero value → stop; Cycle B ~zero marginal
      cost/real value → ship.

---

## The confidence check (both tracks)

- [x] **Stated explicitly** — STOP (high) for Cycle A; SHIP ~75% (deploy-pending) for Cycle B.
- [x] **Confidence matches evidence** — Cycle A kill triangulated (3 robustness variants + Moran's);
      Cycle B bounded by the un-validatable source layer.
- [x] **Conditions named** — trustworthy at 400 m, city-wide, as a sequencing aid; not below 400 m,
      not as health evidence.

---

## The "did we fool ourselves" smell test

- [x] **Does it beat the alternative?** Cycle A beats baselines but **not** the null — and we said
      so, loudly. Cycle B beats density-only.
- [x] **Is it too good?** Cycle A eval R² **0.999** was the red flag — a near-perfect fit screamed
      "validating against your own ingredients." We treated it as suspect and built the external
      test that killed it.
- [x] **Did the number change on re-run?** No — `notebooks/05-evaluation.ipynb` reproduces every
      value exactly (seed 42 throughout; scratch verification = ALL REPRODUCE).
- [x] **Right for the wrong reason?** Caught twice: the presence-AUC=1.0 (circular on effort,
      discounted) and the model itself (right composite, wrong reason — it's sealed surface).
- [x] **Decided the question before the answer?** Yes — T1–T4 and the external pass criteria were
      pre-registered before the build (`phase-4/test-design.md`, `phase-6/allergen-validation-design.md`).

---

## What goes in the report vs the log — satisfied

- Report (`docs/evaluation-report.md`): verdict, results-vs-criteria, compared-to-what, where it
  fails, confidence, NOT-list, recommendation. ✓
- Log (`docs/evaluation-log.md`): all 22 tests incl. the negatives, with what each changed. ✓
- Gallery / audit: `docs/failure-gallery.md` (A) + `docs/validity-audit.md` (B). ✓
- **Every number in the report has a backing log entry.** ✓

---

## Checklist failure modes — none triggered

| Failure | Status |
|---|---|
| No "where it fails" | avoided — gallery + audit |
| Verdict but no confidence | avoided — STOP(high) / SHIP(~75%) |
| Result beats nothing | avoided — explicit baselines/null |
| Report ≠ notebook numbers | avoided — restart-run reproduces all |
| Clean log, all positives | avoided — 3 kills/rejects, 5 weakenings |
| "Causes" with no causal design | avoided — exposure, not outcome |
| Can't reproduce | avoided — fresh-kernel run passes |
