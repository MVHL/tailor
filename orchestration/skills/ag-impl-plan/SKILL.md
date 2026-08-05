---
name: ag-impl-plan
description: Author an Implementation Plan (IP) from acceptance criteria and the test plan — approach, files, reuse, inherited constraints, guardrails, and sequencing, concrete enough that agy executes without re-deriving intent. Run after the test plan; the readiness gate (G2) follows. Use when asked to "plan the implementation" or "how should agy build this".
---

# ag-impl-plan — S6: how agy should build it

You are **Role A / architect**. Do the *thinking*; agy does the *typing*. The plan must be concrete
enough that agy executes it faithfully and a reviewer can check the result against it. This is
`WORKFLOW.md` **S6**.

**The Definition-of-Ready gate is no longer part of this skill** — it is **G2**
(`ag-review-ready`), run by an independent assessor. Do not grade your own plan; write it well
enough to survive that gate.

## Preconditions

`story-<n>.<m>.md` with canonical `AC` (G1 passed) and `TP.md` canonical with red captured. The
tests define what "done" means; plan to make *those* pass.

## Inputs

The `AC`, `TP.md`, the codebase, `.orchestration/glossary.md`, and — if `charter:` is set — the
charter's cross-cutting constraints.

## Procedure

1. **Explore first.** Find the existing functions, modules, and patterns to reuse; name them with
   paths in a **Reuse** list. Use the `Explore` agent or codebase search. Do not let agy reinvent
   what already exists — that is one of the most common and least visible failure modes of
   delegation, because the result passes tests while duplicating the codebase.
2. **Decide the approach and the seam.** Name the bounded context (`COMP#`) the change belongs in
   and call out anything that must cross it. Keep changes inside the seam.
3. **Break into `IM` steps**, each `implements: AC#`, `in: COMP#`. Sequence them so tests can go
   green incrementally rather than all at the end. `touches: <file#symbol>` is filled from the real
   diff at S8, not guessed now.
4. **Cite inherited charter constraints explicitly** in the table — not just inherited, *cited*,
   with how this plan honors each. G2 checks for this, because an unread constraint is the same as
   no constraint.
5. **Write constraints and guardrails:** what agy must not touch, no test weakening, match
   surrounding style, no new dependency or framework, the commit convention (reference realized
   ids), and no merge/push/branch-delete.
6. **Justify an empty reuse list.** "Greenfield module, nothing to reuse" is a legitimate answer;
   silence is not. G2 treats a silently empty list as a finding.
7. **Surface `OQ` and `ASM`.** An `OQ` that would change the **approach** must be resolved before
   delegating — if it needs a human decision, stop and ask, and log the `DEC`. One that would change
   only a detail may be downgraded to an `ASM` and carried, but say which, explicitly.

## Output

`runs/<n>.<m>/IP.md` from `templates/IP.md`. Keep it **alive** through review — update it if the
approach changes during the G3 loop; it is not discarded once written.

## Then stop

Report: the approach in a sentence, `IM` count and their `AC` mapping, what is being reused, and
any `OQ` still open. Next step: `/ag-review-ready <id>` (G2). Nothing reaches agy until that gate
passes.
