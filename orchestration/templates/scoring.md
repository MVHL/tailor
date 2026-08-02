# Scoring rubric — per-step ratings for analytics

Every task emits a `metrics` block into its `RECORD.md` frontmatter so the dashboard can
aggregate quality and cost across tasks over time. Scores are 0–100; each step is graded
by the step that owns it, using the wow grading model (`good`=100, `flagged`=50,
`overdue`/fail=0, mean across items). Keep grading honest — a low score is signal, not
failure; it tells us where the *system* needs improvement.

## Per-step scores

| Step | Score = | Also captured (raw analytics) |
|------|---------|-------------------------------|
| **frame** | 100 if all Assessor coverage checks pass (no orphan R, no bare R, no untestable AC, no P without R, no ask without problem); −20 per failing check class | `grill_rounds` (Q&A cycles), `decisions` (DEC count), `acs` (count), `reframes` (times spec reopened) |
| **plan** | Definition-of-Ready: mean over ACs of (has test? 50) + (has impl step? 50); orphan IM ⇒ that IM scores 0 | `tests_planned`, `red_captured` (bool) |
| **delegate** | first pass green = 100; each extra iteration −25; `blocked` (budget exhausted) = 0; test-cheating detected = 0 (hard fail) | `iterations`, `agy_turns` (Σ num_turns), `timeouts`, `tokens` (Σ usage.total_tokens), `seconds` (Σ duration_seconds) |
| **review** | mean over ACs of good/flagged/overdue (100/50/0); −25 per unresolved security finding (floor 0) | `ac_good`, `ac_flagged`, `ac_overdue`, `security_findings` |

## Overall

`overall_score` = weighted mean: **frame 0.25 · plan 0.15 · delegate 0.25 · review 0.35**.
Review is weighted highest because a passing review is the strongest correctness signal;
frame and delegate matter because spec quality and first-pass rate drive everything else.

Any hard-fail (test-cheating, or `status: blocked`) caps `overall_score` at 40 regardless
of the weighted mean — a task that didn't ship cleanly should never read as healthy.

## Analytics these enable (Phase 2 dashboard)

- **First-pass rate** — share of tasks where `delegate.iterations == 1`.
- **Spec health** — distribution of `frame` scores; `grill_rounds` vs later rework.
- **Cost/time per task** — `delegate.tokens`, `delegate.seconds`, by model.
- **Review burden** — `ac_flagged` + `ac_overdue` trends; security findings over time.
- **Where the system leaks** — which step's score correlates with blocked/reopened tasks.
