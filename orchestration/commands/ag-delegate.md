---
description: S7 — delegate implementation to agy in an isolated worktree: branch, brief, adapter invocation. Judgment happens separately at G3.
argument-hint: "<container-id>  [--iterate]"
---

Delegate **$ARGUMENTS** to agy. Invoke the **ag-delegate** skill.

**Preconditions:** `story`, `TP.md`, `IP.md` all canonical and **G2 passed**. Refuse otherwise and
route to `/ag-review-ready` (or `/ag-frame` if there is no canonical `AC`). This is what enforces
SDD — if asked to "just have agy do X", frame it first.

1. **Isolate** — `git worktree add -b task/<id> .orchestration/worktrees/<id> HEAD`. Ensure the `TP`
   tests exist and are committed on the branch, and **confirm they run RED in the worktree** — not
   just in the author's environment. Write the id to `.orchestration/current-task`.
2. **Brief** — assemble `brief.md` from `templates/brief.md`: glossary + `COMP` terms, `P`/`R`/`NG`
   as context (not scope to revisit), canonical `AC`, the `TP` tests + run command framed as *"these
   exist and currently FAIL — make them pass"*, and the `IP` steps, reuse list, inherited
   constraints, and guardrails. It is a **derived** artifact: if you find yourself deciding something
   while writing it, that decision belongs upstream.
3. **Invoke** via the adapter — **never call `agy` directly**; a direct call leaves no transcript and
   no live marker, so the run is invisible to the board and unauditable afterwards:
   ```bash
   .orchestration/bin/agy-run.sh \
     --brief   .orchestration/runs/<id>/brief.md \
     --dir     .orchestration/worktrees/<id> \
     --run-dir .orchestration/runs/<id> \
     --model   gemini-3.6-flash-high --timeout 15m --iteration 1
   ```
   Parse the `AGY_*` lines. `AGY_EXIT=124` = timeout; non-zero = agy error (read `result.iterN.json`
   `.error`). Record `agy_turns`, `tokens`, `seconds` into the record metrics.
4. **Stop.** Set `TP`/`IP` to `consumed` and report `/ag-review <id>` (G3) as the next step. Do not
   grade the `AC`, do not run tests as judgment, and **do not report success** — agy's self-report is
   never trusted, and it is one step per session.

**`--iterate`** (after a G3 fail verdict): write a **precise** fix brief — name the failing test, the
file, the gap, and paste the **actual** diff and failing output rather than describing them — then
re-invoke with `--iteration N` (the adapter resumes agy's same conversation).

If the fix is *"restore prior behavior"*, attach the real prior commit (`git show <sha> -- <file>`)
as ground truth. Asking agy to re-derive it from prose turns a restore into a fresh implementation
attempt, which has introduced new bugs the working code never had.

**Budget: 3 iterations.** On exhaustion: `RECORD.status: blocked`, `blocked_reason: budget`, log a
`DEC`, escalate with what remains — do not quietly take over and write the code yourself.

Report: what was delegated, the adapter's exit and token/time cost, and the next step.
