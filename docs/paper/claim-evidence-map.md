# Claim–evidence map (living)

**Purpose:** Every sentence in **Abstract** and **Introduction** that sounds like a result must trace to a row here. Update weekly during Phase 2.

**Last updated:** 2026-04-29.

---

## Contribution ↔ claim crosswalk

| Story contribution (`STORY_LOCK.md`) | Primary claims supported |
|-------------------------------------|--------------------------|
| C1 (CBS) | R1, R2 |
| C2 (Lattice + structured outputs) | R5 (audit trail), partially R1 |
| C3 (Temporal + anonymization) | R3, R4 |
| C4 (Predictive validation) | R2, R6 |
| Setup: fees / gross vs net | R7 |

---

## Result rows (numbered for prose: “as predicted (R2)…”)

| ID | Claim (draft wording — tighten at abstract freeze) | Evidence (target) | Status |
|----|-----------------------------------------------------|---------------------|--------|
| R1 | Multi-agent depth has a **breakeven**: below CBS, adding coordination does not justify latency × volatility + costs. | Fig. CBS; Table ablation + CBS column | needs CBS implementation + grid |
| R2 | **CBS** computed from measured graph latency and same-day σ/sec **predicts or ranks** winning ablation on **held-out** periods. | Scatter or calibration; Table with held-out column | needs CBS + pre-registered split |
| R3 | **Temporal cutoff** materially affects measured performance vs an uncapped baseline (lookahead control). | Appendix: cap on/off (same seed, same dates) | needs cap-off experiment |
| R4 | **Anonymization** shifts outcomes or rationale dependence on symbol identity (memorization probe). | A/B table: `ENABLE_ANONYMIZATION` on/off | needs grid |
| R5 | **Structured stage outputs** enable an audit trail from analysts → debate → trader → risk (ablation toggles stages). | Pipeline fig; optional rationale Sankey | lattice exists; rationale fig needs tracker |
| R6 | **Multi-ticker × multi-regime** results support generalization (not one symbol cherry-pick). | Main table × tickers × periods | needs Phase 2 grid |
| R7 | **Net** performance diverges from **gross** under realistic fees. | Table: gross vs net columns | partially supported (`summary.json`) |

---

## Forbidden until supported

Do not assert in camera-ready text:

- “State of the art” vs proprietary desks without a defined benchmark basket.
- Universal “always use full pipeline” without referencing R1 / CBS.
- “Eliminates memorization” — R4 is **mitigation / effect size** only.

---

## Changelog

| Date | Note |
|------|------|
| 2026-04-29 | Initial map seeded from `PAPER_ROADMAP.md` Module 5 + `STORY_LOCK` contributions. |
