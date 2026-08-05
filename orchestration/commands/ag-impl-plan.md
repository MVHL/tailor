---
description: S6 — author the Implementation Plan: approach, IM steps mapped to AC, reuse list, inherited charter constraints, guardrails, and sequencing.
argument-hint: "<container-id>"
---

Author the Implementation Plan for **$ARGUMENTS**. Invoke the **ag-impl-plan** skill.

**Preconditions:** canonical `AC` (G1 passed) and `TP.md` canonical with red captured. The tests
define what "done" means — plan to make *those* pass.

1. **Explore first.** Find the existing functions, modules, and patterns to reuse, and name them with
   paths. Use the `Explore` agent or codebase search. Letting agy reinvent what exists is one of the
   least visible failure modes of delegation: the result passes tests while duplicating the codebase.
2. Decide the **approach** and the **seam** (`COMP#`) — and what must not cross it.
3. Break into **`IM`** steps, each `implements: AC#`, `in: COMP#`, sequenced so tests go green
   incrementally. `touches:` is filled from the real diff at S8, not guessed now.
4. **Cite inherited charter constraints** in the table, with how the plan honors each. An unread
   constraint is the same as no constraint, so G2 checks that they were cited rather than inherited.
5. Write **constraints and guardrails**: what not to touch, no test weakening, match surrounding
   style, no new dependency, the commit convention, no merge/push.
6. An empty reuse list must be **explicitly justified** — G2 treats silence as a finding, because it
   usually means nobody looked.
7. Surface `OQ`/`ASM`. An `OQ` that would change the **approach** must be resolved before delegating
   (stop and ask; log the `DEC`). One that changes only a detail may be downgraded to an `ASM` —
   say which.

Write `runs/<n>.<m>/IP.md` from `templates/IP.md`, and keep it **alive** through the G3 loop — it is
updated if the approach changes, not discarded once written.

**The Definition-of-Ready gate is no longer part of this step.** It is G2
(`/ag-review-ready`), run by an independent assessor — the planner blessing their own plan is the
same Role A/B breach the contract forbids everywhere else.

Report: the approach in a sentence, `IM` count and their `AC` mapping, what is reused, and any open
`OQ`. Next: `/ag-review-ready <id>` (G2).
