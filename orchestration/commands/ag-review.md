---
description: Re-run the review gate on a delegated task (tests + diff + standards/spec review + AC grading) without re-delegating.
argument-hint: "<task-id>"
---

Review task **$ARGUMENTS** as Role B (Assessor), independently — do not trust prior
verdicts or agy's self-report. In the worktree `.orchestration/worktrees/$ARGUMENTS`:

1. Run the `TP.md` tests; capture pass/fail (source of truth).
2. Read the full diff vs HEAD; confirm it realizes `IP.md` and that no tests were weakened
   or deleted to pass.
3. **Spawn a fresh subagent** (Agent/Task) for the judgment pass so the reviewer doesn't
   share the authoring context. Hand it only the diff, `spec.md`, and `TP.md`; have it run
   the `review` skill (standards + spec) and `security-review` if risky.
4. Grade each AC: good / flagged / overdue (the `ticket-execution-review` model), using the
   subagent's verdict to reduce self-scoring bias.

Append the verdict to `review.md`. If gaps remain, recommend another `/ag-delegate` iteration
(if budget remains) or escalation. If clean, recommend `/ag-close $ARGUMENTS`.
