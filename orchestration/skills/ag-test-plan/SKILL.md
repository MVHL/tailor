---
name: ag-test-plan
description: Author a Test Plan (TP) from canonical acceptance criteria BEFORE any code is written (TDD). Produces failing tests that pin each AC to a pass/fail check and a single run command. Use after framing, as the first half of planning, or when asked to "write the test plan" or "plan tests" for a task.
---

# ag-test-plan — tests first

You are Role A. The Test Plan is authored **before** implementation and is what agy is
told to satisfy. No AC may be left without a test.

## Inputs
`.orchestration/runs/<task-id>/spec.md` (the `AC` items), the repo's test framework and
conventions, the glossary.

## Procedure
1. Read every `AC` in the spec. For each, write ≥1 concrete test:
   - `[Happy]` the normal success path.
   - `[Edge]` boundary inputs.
   - `[Error]` invalid input / failure handling.
   - `[Regression]` for bugs: the exact failing case that must stay fixed.
2. Each test states an **observable pass/fail** condition and names **how it is executed**
   (test file + command). Link upward: `covers: AC#`.
3. Detect the repo's test runner (look for existing test config/框架; reuse it — do not
   introduce a new framework). Give ONE command that runs the whole plan.
4. **Write real, executable failing tests into the repo** (in the task worktree if one
   exists, else stage them for `delegate`). Then capture the **red state**: run the
   command, paste the failing output into TP.md. Red proves the tests are meaningful.
5. Assessor check: every AC has ≥1 test; no test is vacuous (a test that passes without
   the feature is worthless). Fix gaps.

## Output
Write `.orchestration/runs/<task-id>/TP.md` from the `templates/TP.md` skeleton, with the
tests, the run command, and the captured red output. The test *files* live in the repo
under test; TP.md is the human-readable plan + proof.

Reuse the `tdd` skill's conventions for structuring red→green.
