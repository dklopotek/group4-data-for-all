# Decision Log — defensible design choices

Consolidated record of the load-bearing decisions across both CRISP-DM cycles, each with its
rationale. (Phase-by-phase detail lives in `phase-6/phase-{1..5}-audit.md` and the design docs.)

| # | Phase | Decision | Rationale | Where |
|---|---|---|---|---|
| 1 | 1 | Frame the decision as *sequencing* committed removals, not *whether* to remove | Maps onto a real standing policy; the cost of being wrong is bounded | paper §5 |
| 2 | 1 | Write a binding cancellation criterion | CRISP-ML(Q); forces an honest stop instead of drift | paper §2.1, §5 |
| 3 | 4A | Five-component additive composite (Cycle A) | Seemed principled — **later proved the flaw** (sealed surface dominated) | paper §3 |
| 4 | 5A | Build an *external* GBIF validation, pre-registered | Don't validate an index against its own ingredients | `phase-5/external-validation-design.md` |
| 5 | 5A | **Stop** the mycorrhizal claim on the null (p=0.99) | Falsification is a result; relabeling would be dishonest | paper §4 |
| 6 | 4B | Multiplicative (not additive) aggregation | Non-compensatory; no hidden weights; matches decision semantics | paper §6.4 |
| 7 | 2B | Downgrade source to a proxy (no measured pollen exists) | Cancellation criterion firing; honesty over false validation | paper §6.2 |
| 8 | 5B | Layer-audition gate (re-order AND non-redundant); reject 3 layers | Make every layer earn its place; report rejections | paper §7.3 |
| 9 | 6 | Deploy at **census-section** grain, not barri (73) or 400 m (494) | Sections are finer AND the native demand grain → drops interpolation | `section-street-design.md` D1 |
| 10 | 6 | Mature set = {EXEMPLAR, PRIMERA} (A1), sensitivity-tested | Largest size classes ≈ highest pollen; tested as T4 arm | `section-street-design.md` A1 |
| 11 | 6 | Street output is action/inventory only, **no priority column** | Ecological fallacy; street-level priority is invented precision | honesty gate C2 |
| 12 | 6 | Report the section-grain T1/T4 **failure** honestly (MAUP) | Pre-registration is binding; don't re-tune to pass | paper §8.2 |
| 13 | 6 | Build the interactive map despite the no-UI course rule | User's explicit call ("go full on"); flagged as out-of-scope aid | `build_deploy_map.py` header |
| 14 | 6 | DOI/Zenodo left PENDING, not faked | Requires team institutional accounts; honesty | `publication_plan.md` |
