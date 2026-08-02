---
description: Run the full orchestration loop on an idea or PRP — frame → plan → delegate → review → record — autonomously, stopping only for real decisions.
argument-hint: "<idea, PRP paste/link, or bug report>"
---

Run the whole loop for: **$ARGUMENTS**

You are the Conductor. Execute end-to-end, following the autonomy contract in `CLAUDE.md`:
proceed without asking unless the problem/scope is ambiguous, requirements conflict, there's
no AC for something you'd build, an action is irreversible/outward-facing, or agy exhausts
its iteration budget. Log every human exchange as a `DEC`.

1. **Frame** — `ag-frame` skill → `spec.md`. Grill until it holds. (This is where the human's
   attention is spent; stop and ask on real decisions.)
2. **Plan** — `ag-test-plan` → `TP.md` (tests first, red captured), then `ag-impl-plan`
   → `IP.md`. Run the Definition-of-Ready gate.
3. **Delegate** — `ag-delegate` skill: worktree, brief, adapter, bounded review loop.
4. **Record & close** — write `RECORD.md` (with the mandatory assumptions/problems/bugs/
   issues section), update `graph.md` + `runs/index.md`, merge the worktree, commit.

If not yet onboarded (no `.orchestration/`), run `/ag-init` first.

At the end, report: the branch/diff, AC pass/fail, and the four closing-section highlights.
