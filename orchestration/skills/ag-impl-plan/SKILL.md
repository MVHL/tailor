---
name: ag-impl-plan
description: Author an Implementation Plan (IP) from acceptance criteria — the approach, files, reuse, constraints, and sequencing agy needs to build without re-deriving intent. Use after the test plan, as the second half of planning, or when asked to "plan the implementation" or "how should agy build this".
---

# ag-impl-plan — how agy should build it

You are Role A / architect. Produce a plan concrete enough that agy executes it faithfully
and a reviewer can check the result against it. Do the *thinking*; agy does the *typing*.

## Inputs
`spec.md` (AC), `TP.md` (the tests to satisfy), the codebase, the glossary.

## Procedure
1. **Explore first.** Find existing functions, modules, and patterns to reuse — do not let
   agy reinvent what exists. Name them with paths in a "Reuse" list. (Use the `Explore`
   agent or codebase search.)
2. Decide the **approach** and the **bounded context** (`COMP#`) the change belongs in.
   Keep changes within that seam; call out anything that must cross it.
3. Break into `IM` steps, each linked `implements: AC#`, `in: COMP#`, and (after
   delegation) `touches: <file#symbol>`. Sequence them so tests can go green incrementally.
4. Write **constraints & guardrails**: what agy must NOT touch, the commit convention
   (reference realized ids), style to match, security/perf limits.
5. Surface **blockers/open questions**. If a blocker needs a human decision, stop and ask
   (log a `DEC`) rather than guessing.

## Output
Write `.orchestration/runs/<task-id>/IP.md` from `templates/IP.md`. Keep it alive through
review — update it if the approach changes.

## Definition-of-Ready gate (run before delegating)
Re-run the Assessor coverage checks over spec + TP + IP together:
- every `AC` has a test (`covers:`) **and** an impl step (`implements:`);
- no orphan `IM` (an `IM` with no `implements:`);
- no `AC` left unplanned.
Fail = fix before `delegate`. This is what makes delegation safe.
