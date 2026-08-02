---
description: The one command to remember. Detects where a task is (or that it's new) and does the right next step through to done — no need to recall the individual steps.
argument-hint: "<idea/PRP/bug>  OR  <task-id>  OR  (nothing to see status)"
---

You are the Conductor. Figure out the correct next action from the repo/task **state** and
do it — the human should not have to remember the pipeline. Input: **$ARGUMENTS**

## Dispatch logic

1. **Not onboarded?** If `.orchestration/` is missing → run `orchestrate-init` first, then continue.

2. **No argument?** Print a status overview: read every `.orchestration/runs/*/RECORD.md`
   (and in-flight run dirs without a RECORD), and show a table — task · stage · status ·
   overall_score · what's next. Then stop. (This is the local mirror of the dashboard.)

3. **Argument matches an existing run** (`.orchestration/runs/<id>/` exists, or fuzzy-matches
   one) → **resume** it. Detect the current stage and run the next step:
   - `spec.md` missing → `ag-frame`
   - `spec.md` present, `TP.md`/`IP.md` missing or DoR not passed → `ag-plan`
   - planned but no green review (no `RECORD` or `status: in-review`) → `delegate` (which
     includes the review loop)
   - review clean, not closed → `ag-close`
   - `status: blocked` / `awaiting-decision` → summarize exactly what's needed and stop.
   Then keep advancing through the remaining stages to completion.

4. **Argument is a new idea/PRP/bug** (no matching run) → mint a `<task-id>` and run the
   **full loop**: `ag-frame → ag-plan → ag-delegate → ag-close`.

## Rules

- Honor the autonomy contract in `CLAUDE.md`: run to done without asking, EXCEPT stop for
  ambiguous scope, conflicting requirements, a missing AC, an irreversible/outward action,
  or agy exhausting its iteration budget. Log every human exchange as a `DEC`.
- Announce each stage you enter ("Framing…", "Delegating iteration 2…") so progress is visible.
- Never skip the Definition-of-Ready gate before delegating, or the review gate before closing.

At the end, report: stage reached, AC pass/fail, `overall_score`, and (if stopped) exactly
what you need from the human. The granular commands (`/ag-frame`, `/ag-plan`, `/ag-delegate`,
`/ag-review`, `/ag-close`) remain available for manual control; `/ag` is the
default entry point.
