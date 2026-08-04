# Scoring rubric — content quality, not throughput

Two scores describe a task, and both are **derived from countable evidence** so they can be
recomputed by the board at any time rather than being asserted by whoever closed the task:

| Score | Answers | Computed from |
|-------|---------|---------------|
| **Framing score** | *How well is the problem framed and traced?* | the parsed `P/R/NG/AC/T/IM` item graph (spec.md + TP.md + IP.md) |
| **Output score** | *How good is what came out?* | the closing record's sections + review grading in `RECORD.md` |

The guiding property: **a low score must mean more real problems.** Every deduction is tied
to a countable item (a bug, a finding, an uncovered AC), never to a vibe. If two tasks score
80 and 95, the 80 has strictly more recorded problems.

---

## 1. Framing score (input quality)

Computed live by the board — no need to wait for close, so a weak spec is visible *before*
delegation. Each check is a **ratio** (share of items that pass), not a boolean, so the score
degrades in proportion to how many items are broken.

| Check | Ratio | Weight |
|-------|-------|--------|
| Every problem has a requirement | `P` with ≥1 `R` solving it / all `P` | 1.0 |
| No orphan requirement | `R` tracing to ≥1 `P` / all `R` | 1.0 |
| Every requirement has an AC | `R` covered by ≥1 `AC` / all `R` | 1.0 |
| No orphan AC | `AC` covering ≥1 `R` / all `AC` | 1.0 |
| Every AC has a test | `AC` covered by ≥1 `T` / all `AC` | 1.2 |
| Every AC has an impl step | `AC` with ≥1 `IM` / all `AC` | 1.0 |
| Scope bounded | any `NG` recorded | 0.5 |

`framing_score` = weighted mean of the ratios × 100. Checks whose artifact doesn't exist yet
(no TP → no test check) are **skipped**, not failed — a task mid-planning isn't punished for
work it hasn't reached.

This is the Definition-of-Ready gate made continuous: 100 means every problem leads to a
requirement, every requirement to an AC, and every AC to both a test and an impl step.

## 2. Output score (result quality)

The headline number. A weighted mean of **sub-scores**, each driven by counted findings from
the closing record. The overall is only ever a reflection of its sections.

| Dimension | Weight | Score |
|-----------|-------:|-------|
| **Acceptance** | 0.30 | `(good + 0.5·flagged) / graded` × 100; if no per-AC grading, 100/0 on tests pass/fail |
| **Tests** | 0.25 | pass = 100, fail = 0; −25 if green with no captured red state |
| **Defects** | 0.20 | 100 − 25 × *possible bugs* |
| **Security** | 0.10 | 100 − 34 × *unresolved findings* |
| **Assumptions & risk** | 0.08 | 100 − 12 × *assumptions* − 8 × *discovered problems* |
| **Open follow-ups** | 0.07 | 100 − 15 × *open issues* |

All dimensions clamp to 0–100. Dimensions with no evidence are skipped and the weights
renormalise over what's present.

**Caps.** `status: blocked` or `tests: fail` caps the overall at **40** — a task that didn't
ship cleanly must never read as healthy, however good its other sections are.

**Overriding a dimension.** Judgement sometimes beats arithmetic (e.g. three trivial
follow-ups shouldn't sink a good task). Set it explicitly in `RECORD.md`:

```yaml
metrics:
  quality: { followups: 90, defects: 60 }   # only the keys you override
```
Overrides are shown on the board as "set in RECORD" so they stay honest and reviewable.

**Why counts, not adjectives.** Deductions per *item* are what make the scale meaningful:
a task with 6 open issues (followups 10) genuinely carries more unfinished work than one with
1 (85). If a count feels unfair, the fix is usually to close or re-scope the item — not to
soften the rubric.

## 3. Process metrics (raw analytics — no longer the headline)

Still captured in `RECORD.md` for trend analysis, but deliberately **excluded** from the
output score: they measure how the work went, not how good the result is. A task that took
three iterations but shipped clean, well-tested code is a *good outcome* with an expensive
path — the board shows both rather than blending them into one misleading number.

| Step | Captured |
|------|----------|
| frame | `grill_rounds`, `decisions`, `acs`, `reframes` |
| plan | `tests_planned`, `red_captured` |
| delegate | `iterations`, `agy_turns`, `timeouts`, `tokens`, `seconds` |
| review | `ac_good`, `ac_flagged`, `ac_overdue`, `security_findings` |

`red_captured` and the review counts feed the output score above; the rest are analytics only.

**Test-cheating remains a hard fail.** If any iteration gamed a test (fabricated or vacuous
assertions, invisible markers), record it under *Discovered problems* and set
`metrics.quality.tests: 0` — the Tests dimension is the honest place for it, and its 0.25
weight plus the acceptance dimension will drag the overall down accordingly.

## Analytics these enable

- **Spec health** — framing score distribution; framing score vs. later iteration count.
- **Where quality leaks** — which output dimension is consistently lowest across tasks.
- **Cost/time per task** — `delegate.tokens` / `seconds`, by model.
- **Rework** — `iterations` vs. output score: does slower actually buy better?
