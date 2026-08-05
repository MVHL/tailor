---
description: RETIRED — S5 and S6 now run as separate steps. Use /ag-test-plan then /ag-impl-plan (or just /ag).
argument-hint: "<container-id>"
---

**`/ag-plan` is retired.** Planning is two separately-scored steps with a gate after them, because a
single combined step could not be evaluated or improved independently — see `WORKFLOW.md` §4.

For **$ARGUMENTS**, do this instead:

1. `/ag-test-plan <id>` — S5, tests first with the red state captured.
2. `/ag-impl-plan <id>` — S6, approach and `IM` steps.
3. `/ag-review-ready <id>` — G2, the Definition-of-Ready gate, run by an independent assessor rather
   than by the planner.

Or simply `/ag <id>`, which advances whichever of these is next.

Do not try to do S5 and S6 in one pass: the Impl Plan is written **against** the Test Plan, so the
tests must exist and be red first. Tell the user this command is retired, then run the correct step.
