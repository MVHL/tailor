---
description: Close a reviewed task — write the audit RECORD, update the graph/index, merge the worktree (Conductor owns the merge).
argument-hint: "<task-id>"
---

Close task **$ARGUMENTS**. Only proceed if the review gate is clean (else say why and stop).

1. **RECORD** — write `.orchestration/runs/$ARGUMENTS/RECORD.md` from `templates/RECORD.md`.
   Fill the frontmatter (status `done`, iterations, acs, realizes, comp, tests, timestamps,
   branch) and the body. The **closing section is mandatory** — write all four, using
   "None." where empty:
   - **Assumptions** (from the SIG/ASK trail + planning)
   - **Discovered problems** (out-of-scope issues found)
   - **Possible bugs** (suspected, unconfirmed — how to reproduce)
   - **Open issues** (follow-ups, deferred Non-Goals, tech debt)
2. **Metrics** — fill the `metrics` block in the frontmatter per `templates/scoring.md`.
   Compute the four per-step scores and `overall_score`; pull raw analytics (agy_turns,
   tokens, seconds) by summing `.num_turns`, `.usage.total_tokens`, `.duration_seconds`
   across the run's `result.iter*.json` files. Be honest — a low score is signal.
3. **Graph** — update `.orchestration/graph.md`: add the `RUN`, the `touches:` anchors from
   the diff, any new `FEAT`/`COMP`, and `DEC` rows. Append a row to `runs/index.md`.
4. **Merge** — you own the merge (agy never merges). Fast-forward/merge `task/$ARGUMENTS`
   into the working branch, run the tests once more on the merged result, then remove the
   worktree with `git worktree remove --force .orchestration/worktrees/$ARGUMENTS`
   (`--force` because build/test byproducts like `__pycache__` are expected there; the
   code changes are already merged) and `git worktree prune`.
5. Commit the run directory + graph + index. Show the diff and confirm before committing if
   anything is destructive.

Report: what shipped, the four closing-section highlights, and the record path.
