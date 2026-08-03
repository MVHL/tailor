---
name: ag-delegate
description: Delegate an implementation task to the agy (Antigravity) CLI in an isolated git worktree, then review its output against the Test Plan and acceptance criteria in a bounded loop until done. The core delegation engine of the orchestration system. Use after planning (TP+IP exist), or when asked to "delegate", "hand this to agy", or "have agy implement" a framed task.
---

# ag-delegate — hand off, then review until done

You are **Role B (Assessor)** here: you delegate the typing to agy, then verify its work
adversarially. **Never trust agy's self-reported success** — the git diff and the test
run are the source of truth.

## Preconditions (refuse if unmet)
`spec.md`, `TP.md`, `IP.md` all exist for `<task-id>` and passed the Definition-of-Ready
gate. No canonical AC → stop and route to `ag-frame`. This enforces SDD.

## The adapter
Call `.orchestration/bin/agy-run.sh` (copied in by `orchestrate-init`; falls back to
`agy-run` on PATH). It wraps `agy -p` with worktree scoping, JSON output, transcript
capture, and conversation continuity. Never call `agy` directly.

## Procedure

### 1. Isolate
```bash
git worktree add -b task/<task-id> .orchestration/worktrees/<task-id> HEAD
```
Ensure the failing tests from `TP.md` exist in the worktree (commit them on the branch if
`ag-test-plan` staged them). Confirm they run RED there.

### 2. Assemble the brief
Build `.orchestration/runs/<task-id>/brief.md` from `templates/brief.md`: paste the
relevant glossary terms, the P/R/NG, the AC, the **TP tests + run command** (framed as
"these exist and currently fail — make them pass"), and the IP steps/constraints. Be
explicit that agy must not weaken tests, must reuse named utilities, must not merge/push,
and must reference realized ids in commits.

### 3. Delegate (iteration 1)
```bash
.orchestration/bin/agy-run.sh \
  --brief .orchestration/runs/<task-id>/brief.md \
  --dir   .orchestration/worktrees/<task-id> \
  --run-dir .orchestration/runs/<task-id> \
  --model gemini-3.6-flash-high --timeout 15m --iteration 1
```
Parse the `AGY_*` output lines. `AGY_EXIT=124` = timeout; non-zero = agy error (read
`result.iterN.json` `.error`).

### 4. Review (the gate) — use an INDEPENDENT reviewer
Real Role A/B separation: you authored the spec, so you must not be the sole judge of the
result. Run the objective checks yourself, then **spawn a fresh subagent** (the `Task`/
`Agent` tool, or the `review` skill inside a subagent) that has NOT seen the framing
rationale — give it only the diff, `spec.md`, and `TP.md` and ask: "does this diff satisfy
these ACs and tests, and what's wrong with it?" Its independence is the point.

Objective checks (you run these — they are mechanical, not judgment):
1. **Run the TP tests.** Capture green/red. This is decisive.
2. **Read the diff** (`git -C <worktree> diff HEAD`). Did agy edit or delete tests to
   cheat? (If so, reject outright.)

Independent judgment (the subagent):
3. Standards + spec review (the `review` skill). `security-review` on risky changes.
4. Grade each AC: **good** (passing test + clean impl) / **flagged** (works but issues) /
   **overdue** (not done). Use the `ticket-execution-review` model. The subagent's grades
   feed the `review` metrics — prefer them over your own to avoid self-scoring bias.

### 5. Loop (bounded)
If any AC is not **good**:
- Write a precise fix instruction (name the failing test, the file, the gap) to a new
  brief and re-invoke the adapter with `--iteration N` (it auto-resumes agy's
  conversation). Keep the diff and failing output in the instruction.
- **Default budget: 3 iterations.** On exhaustion, STOP and escalate to the human with a
  crisp summary of what remains; set `RECORD.status: blocked`. Log a `DEC`.

### 6. Definition-of-Done
Pass only when: every AC has a passing test (red→green observed), the diff realizes the
IP, and review is clean. Append the actual `touches: <file#symbol>` anchors to `IP.md`
and `graph.md` from the diff.

## Output
Append the iteration log and review verdicts to
`.orchestration/runs/<task-id>/review.md`. Leave the worktree in place for `ag-close`
to merge (the Conductor owns the merge — agy never does).
