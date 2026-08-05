# Scoring rubric — derived, per-artifact, recomputable

Every number here is **derived from countable evidence in the files**, so the board can recompute
all of it at any time rather than trusting whoever closed the task. See `WORKFLOW.md` §8, which
this document implements.

The guiding property: **a low score must mean more real problems.** Every deduction ties to a
countable item — a finding, a bug, an uncovered `AC` — never to a vibe. If two items score 80 and
95, the 80 has strictly more recorded problems.

Three levels, each derived from the one below.

---

## 1. Artifact score — the atom

```
artifact_score = (weighted mean of its canonical-when ratios × 100)
                 − 10 × (findings attributed to it that are open or waived)
                 clamped to 0–100
```

Each check is a **ratio** (share of items that pass), never a boolean, so the score degrades in
proportion to how much is broken. Checks whose artifact does not exist yet are **skipped, not
failed** — an item mid-planning is not punished for work it has not reached.

| Artifact | Checks (each a ratio) | Weight |
|----------|----------------------|-------:|
| `prp` | `SIG` verbatim + sourced · `ASK` links a `SIG` · `P` cites evidence · `P` has ≥1 `R`/`NG` | 1.0 |
| | `discovery_coverage` (answered ÷ applicable aspects) | 1.2 |
| `spike` | `D`/`RK` link their `P#` · owner / likelihood+impact stated | 1.0 |
| `prd` | no orphan `R` · every `R` has ≥1 `AC` · every `NG` has `excludes: P#` · ≥1 `NG` | 1.0 |
| | `D`/`RK` visibly factored into `R`/`NG` | 0.6 |
| `story` | every `AC` has `covers: R#` · every `AC` observable+testable · `R` subset resolves upward | 1.0 |
| `tp` | every `AC` has ≥1 `T` | 1.2 |
| | happy/edge/error present per `AC` · non-vacuity stated per `T` | 0.8 |
| | **`red_captured`** | 1.0 |
| `ip` | every `AC` has ≥1 `IM` · no orphan `IM` | 1.0 |
| | reuse list non-empty or justified · charter constraints cited | 0.6 |
| `charter` | appetite declared · ≥1 `BND` · every `SL` has hypothesis + `reduces:` · every `SL` vertical · `SL1` reduces top `UNK` · `needs:` acyclic · `review_after` set | 1.0 |
| `review-*` | every input artifact has a verdict · every `F` attributed to a step · every `F` fixed or waived-with-`DEC` | 1.0 |

## 2. Step score

```
step_score = mean(artifact_score for that step's OUT artifacts)
```

**This is the number that makes a step independently improvable.** *"Discovery averages 62 across
9 epics"* is actionable; *"task scored 78"* never was.

## 3. Roll-ups

| Roll-up | From |
|---------|------|
| **Framing score** | Phase A + Phase B step scores (S1–S6, G1, G2) |
| **Output score** | the dimensions in §4 below, driven by G3 + S8 |
| **Charter health** | the `charter` row in §1, plus `appetite_burn` and `thesis_held` |

**Charter health is deliberately *not* a roll-up of its children.** A charter can be full of
well-framed, cleanly-shipped slices and still be a losing bet — that is what the bet log records.
Averaging the children would hide exactly the failure the re-bet exists to catch.

---

## 4. Output dimensions (result quality)

A weighted mean of sub-scores, each driven by counted findings from the closing record. The
overall is only ever a reflection of its parts.

| Dimension | Weight | Score |
|-----------|-------:|-------|
| **Acceptance** | 0.30 | `(good + 0.5·flagged) / graded` × 100; if no per-`AC` grading, 100/0 on tests pass/fail |
| **Tests** | 0.25 | pass = 100, fail = 0; **−25 if green with no captured red state** |
| **Defects** | 0.20 | 100 − 25 × *possible bugs* |
| **Security** | 0.10 | 100 − 34 × *unresolved security findings* |
| **Assumptions & risk** | 0.08 | 100 − 12 × *open `ASM`* − 8 × *discovered problems* |
| **Open follow-ups** | 0.07 | 100 − 15 × *open `OQ`* |

All dimensions clamp to 0–100. Dimensions with no evidence are skipped and the weights
renormalise over what is present.

**Caps.** `status: blocked` or `tests: fail` caps the overall at **40** — an item that did not
ship cleanly must never read as healthy, however good its other sections are.

**Overriding a dimension.** Judgement sometimes beats arithmetic (three trivial follow-ups should
not sink a good task). Set it explicitly in `RECORD.md`:

```yaml
metrics:
  quality: { followups: 90, defects: 60 }   # only the keys you override
```

Overrides render on the board as *"set in RECORD"* so they stay reviewable.

**Test-cheating is a hard fail.** If any iteration gamed a test — fabricated or vacuous
assertions, invisible markers — record it under *Discovered problems* and set
`metrics.quality.tests: 0`.

---

## 5. Rejected items are excluded

A `rejected` item is **left out of the framing and output score distributions entirely**. Scoring
it would punish the workflow for working (`WORKFLOW` R12). What is tracked instead:

| Pattern | Reading |
|---------|---------|
| rejections concentrated at **S2 / S2b** | healthy — the cheap gates are doing their job |
| rejections at **HG1** | scope discipline working, but Discovery surfaced worth-questions late |
| rejections at **G2 / G3** | a **defect**: every upstream step missed it. Investigate the step, not the item |
| a charter with most slices rejected at **S2b** | the *thesis* is wrong, not the slices — trigger a re-bet |

---

## 6. Process metrics (analytics only — deliberately not scored)

These measure how the work went, not how good the result is. A task that took three iterations
but shipped clean, well-tested code is a *good outcome* with an expensive path — the board shows
both rather than blending them into one misleading number.

| Group | Captured |
|-------|----------|
| frame | `grill_rounds`, `acs`, `reframes` |
| plan | `tests_planned`, `red_captured` |
| delegate | `iterations`, `agy_turns`, `timeouts`, `tokens`, `seconds` |
| gates | per gate: `rounds`, `findings_raised`, `findings_waived`, `attributed` |
| human | `touches` (target 3), `hg1_latency_h`, `hg2_latency_h`, `interrupts`, `assumptions_waived` |
| autonomy | `auto_approved`, `auto_approval_failed` |

`red_captured` and the G3 counts feed the output score above; the rest are analytics.

---

## 7. The analytics this enables

- **The intake hypothesis.** `discovery_coverage` should predict downstream `interrupts`, G1
  findings attributed to S2, and G3 iteration count. If thin intake does **not** show up
  downstream, the coverage checklist is measuring the wrong aspects and should be retuned. This
  is the single most valuable number the board can produce.
- **Where quality leaks** — which output dimension is consistently lowest across items.
- **Which step causes rework** — `gates.*.attributed` summed by step.
- **Is the automation real** — `human.touches` vs. target 3; `interrupts` per step.
- **Is auto-approval safe** — `auto_approved` vs. `auto_approval_failed`. Non-zero failure means
  tighten the conditions, not explain them away.
- **Cost/time per task** — `delegate.tokens` / `seconds`, by model.
- **Approval backlog vs. engineering backlog** — items `blocked` with `blocked_reason: approval`.
