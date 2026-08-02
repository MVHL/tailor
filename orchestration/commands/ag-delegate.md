---
description: Delegate a planned task to agy in an isolated worktree and review its output until done (bounded loop).
argument-hint: "<task-id>"
---

Delegate task **$ARGUMENTS** to agy. Requires `spec.md`, `TP.md`, `IP.md` that passed the
Definition-of-Ready gate — refuse and route to `/ag-plan` if not.

Invoke the **ag-delegate** skill: create the worktree, assemble `brief.md`, run the
adapter, then review (run tests, read diff, `review` skill, grade each AC). Loop on the
same agy conversation up to the iteration budget (default 3); on exhaustion, stop and
escalate to the human with what remains and set the record status to `blocked`.

Report per-iteration verdicts. When every AC is green (red→green observed, diff realizes
the IP, review clean), tell the user it's ready for `/ag-close $ARGUMENTS`.
