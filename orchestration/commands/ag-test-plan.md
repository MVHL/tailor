---
description: S5 — author the Test Plan from canonical AC: real failing tests in the repo, one run command, and the captured red state that proves they measure something.
argument-hint: "<container-id>"
---

Author the Test Plan for **$ARGUMENTS**. Invoke the **ag-test-plan** skill.

**Preconditions:** `story-<n>.<m>.md` with **canonical** `AC` and **G1 passed**. If G1 has not passed,
stop and route to `/ag-review-framing` — writing tests against un-gated criteria is how you end up
testing the wrong thing precisely.

1. For each `AC`, write ≥1 concrete test — `[Happy]`, `[Edge]`, `[Error]`, plus `[Regression]` for
   bugs. Each with an observable pass/fail condition, its test file, and `covers: AC#`. If a category
   is genuinely inapplicable, say which and why rather than omitting it silently.
2. **Reuse the repo's existing runner and conventions.** Introduce no new framework, runner, or
   assertion library. Give **one** command that runs the whole plan.
3. **Write real executable failing tests into the repo** — in the task worktree if one exists, else
   staged for `/ag-delegate` to commit on the task branch. Files that run, not pseudocode.
4. **Capture the red state:** run the command and paste the **actual failing output** into `TP.md`.
   Set `red_captured: true` only when that output is genuine.
5. **Fill the non-vacuity table** — for each test, one line on why it cannot pass without the
   feature. This catches the most expensive failure in the system: a test that already passes, which
   then makes a do-nothing diff look green at G3.
6. If an `AC` cannot be pinned to a pass/fail check at reasonable cost, **that is a defect in the
   `AC`**. Open an `OQ` (`affects: AC#`) and send it back to be reworded. Never write a weak test to
   make a vague criterion look covered.

Write `runs/<n>.<m>/TP.md` from `templates/TP.md`.

Report: tests per `AC`, the run command, the captured red failure count, and any `OQ` raised against
an `AC`. Next: `/ag-impl-plan <id>` (S6). Do not write implementation code, and do not run G2
yourself.
