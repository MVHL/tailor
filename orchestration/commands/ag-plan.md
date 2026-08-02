---
description: Plan a framed task — author Test Plan (tests first) then Impl Plan, and run the Definition-of-Ready gate.
argument-hint: "<task-id>"
---

Plan task **$ARGUMENTS**. Requires `.orchestration/runs/$ARGUMENTS/spec.md` (run `/ag-frame` first if missing).

1. Invoke **ag-test-plan** → `TP.md` (+ real failing tests, red state captured).
2. Invoke **ag-impl-plan** → `IP.md` (explore the codebase for reuse first).
3. Run the **Definition-of-Ready gate**: every AC has a test AND an impl step; no orphan
   R/IM; every AC testable. If it fails, fix and re-check — do not proceed.

Report the gate result. When green, tell the user it's ready for `/ag-delegate $ARGUMENTS`.
