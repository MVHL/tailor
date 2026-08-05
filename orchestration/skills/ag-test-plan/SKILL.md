---
name: ag-test-plan
description: Author a Test Plan (TP) from canonical acceptance criteria BEFORE any code is written (TDD) — real failing tests in the repo, one run command, and the captured red state that proves they measure something. Run after the framing gate and before the impl plan. Use when asked to "write the test plan", "plan tests", or start planning a framed task.
---

# ag-test-plan — S5: tests first

You are **Role A**. The Test Plan is authored **before** implementation and is what agy is told to
satisfy. No `AC` may be left without a test. This is `WORKFLOW.md` **S5**.

You do not gate your own plan — **G2** (`ag-review-ready`) does, after S6.

## Preconditions (refuse if unmet)

`story-<n>.<m>.md` exists with **canonical** `AC` and **G1 has passed**. No blessed `AC` → route to
`ag-frame` / `ag-review-framing`. Writing tests against un-gated criteria is how you end up testing
the wrong thing precisely.

## Inputs

The story's `AC`, the repo's existing test framework and conventions, `.orchestration/glossary.md`.

## Procedure

1. **Read every `AC`.** For each, write ≥1 concrete test:
   - `[Happy]` the normal success path
   - `[Edge]` boundary inputs
   - `[Error]` invalid input / failure handling
   - `[Regression]` for bugs: the exact failing case that must stay fixed
   Each `AC` should carry happy + edge + error unless one is genuinely inapplicable — then say
   which and why, rather than silently omitting it.
2. **Each test states an observable pass/fail condition** and names how it is executed (test file
   path). Link upward: `covers: AC#`.
3. **Detect the repo's runner** — look for existing test config and conventions and **reuse them**.
   Do not introduce a new framework, runner, or assertion library. Give **one** command that runs
   the whole plan.
4. **Write real, executable failing tests into the repo** — in the task worktree if one exists,
   else stage them for `ag-delegate` to commit on the task branch. Not pseudocode: files that run.
5. **Capture the red state.** Run the command and paste the **actual failing output** into `TP.md`.
   Red is what proves the tests are meaningful, so this is evidence, not ceremony. Set
   `red_captured: true` only when the pasted output is genuine.
6. **Fill the non-vacuity table.** For each test, one line on *why it cannot pass without the
   feature*. This is the check that catches the most expensive failure mode in the whole system:
   a test that passes against the unmodified codebase, which then makes a do-nothing diff look
   green at G3.
7. **Report untestable `AC` as a finding, do not work around it.** If an `AC` cannot be pinned to a
   pass/fail check at reasonable cost, that is a defect in the `AC` — open an `OQ`
   (`affects: AC#`) and send it back to be reworded. Never write a weak test to make a vague
   criterion look covered; that is the single easiest way to make the whole gate chain meaningless.

Reuse the `tdd` skill's conventions for structuring red→green.

## Output

`runs/<n>.<m>/TP.md` from `templates/TP.md` — frontmatter (`inputs:` listing the `AC` it covers,
`run_command`, `red_captured`), the tests, the run command, the pasted red output, and the
non-vacuity table. The test **files** live in the repo under test; `TP.md` is the human-readable
plan plus the proof.

## Then stop

Report: tests per `AC`, the run command, that red was captured (with the failure count), and any
`OQ` raised against an `AC`. Next step: `/ag-impl-plan <id>` (S6). Do not write implementation code
and do not run G2 yourself.
