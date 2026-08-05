---
name: ag-delegate
description: Delegate implementation to the agy (Antigravity) CLI in an isolated git worktree — create the branch, assemble the brief from the story/TP/IP, invoke the adapter, and re-invoke with a precise fix brief on each G3 iteration. Requires the readiness gate to have passed. Use when asked to "delegate", "hand this to agy", or "have agy implement" a planned task.
---

# ag-delegate — S7: hand off the typing

You **isolate, brief, and invoke**. You do **not** judge the result: that is **G3**
(`ag-review-code`), run by an independent sub-agent. This is `WORKFLOW.md` **S7**.

The loop is `S7 → G3 → S7 → …`, bounded at **3 iterations**. This skill performs each invocation;
G3 issues each verdict and the fix instruction.

## Preconditions (refuse if unmet)

`story-<n>.<m>.md`, `TP.md`, `IP.md` all **canonical** and **G2 passed**. No canonical `AC` → route
to `ag-frame`. G2 not passed → route to `ag-review-ready`. This is what enforces SDD; if asked to
"just have agy do X", frame it first.

## The adapter

Call `.orchestration/bin/agy-run.sh` (falls back to `agy-run` on PATH). It wraps `agy -p` with
worktree scoping, JSON output, transcript capture, conversation continuity, and the live
`running.json` marker. **Never call `agy` directly** — a direct call leaves no transcript and no
live state, so the run is invisible to the board and unauditable afterwards.

## Procedure

### 1. Isolate

```bash
git worktree add -b task/<n>.<m> .orchestration/worktrees/<n>.<m> HEAD
```

Ensure the failing tests from `TP.md` exist in the worktree and are committed on the branch (if S5
staged them, commit them now). **Confirm they run RED there** — red in the worktree, not just in the
author's environment. Write the container id to `.orchestration/current-task` so sub-agent
breadcrumbs nest correctly.

### 2. Assemble the brief

Build `runs/<n>.<m>/brief.md` from `templates/brief.md`. It is a **derived** artifact — mechanical
assembly, no new judgment, no score of its own:

- the relevant **glossary** terms and `COMP` definitions, so agy uses the right words
- `P` / `R` / `NG` as **context, not scope to revisit**
- the canonical `AC` — the definition of done
- the **`TP` tests + the one run command**, framed as *"these exist and currently FAIL — make them
  pass"*
- the `IP` steps, reuse list, inherited charter constraints, and guardrails

Be explicit that agy must not weaken, skip, or delete tests; must reuse the named utilities; must
not merge, push, or delete branches; and must reference realized ids in commits.

### 3. Invoke (iteration 1)

```bash
.orchestration/bin/agy-run.sh \
  --brief   .orchestration/runs/<n>.<m>/brief.md \
  --dir     .orchestration/worktrees/<n>.<m> \
  --run-dir .orchestration/runs/<n>.<m> \
  --model   gemini-3.6-flash-high --timeout 15m --iteration 1
```

Parse the `AGY_*` output lines. `AGY_EXIT=124` = timeout; non-zero = agy error (read
`result.iterN.json` `.error`). Record `agy_turns`, `tokens`, `seconds` into the record's metrics.

**Never trust agy's self-report.** The JSON envelope is for monitoring and audit only; the git diff
and the test run are the source of truth. Do not summarize agy's claims as if they were results —
hand the diff to G3 and let it decide.

### 4. Hand to G3, then stop

Set `TP.md` / `IP.md` to `consumed`, and report `/ag-review <id>` as the next step. Do not run the
tests-as-judgment yourself, do not grade the `AC`, and do not report success — one step per session.

### 5. Iterate (`--iterate`, on a G3 fail verdict)

Given G3's fix instruction:

1. Write a **precise** fix brief: name the failing test, the file, and the gap. Include the actual
   diff and failing output — not a prose description of them.
2. Re-invoke the adapter with `--iteration N`; it auto-resumes agy's **same conversation**.
3. **If the fix is "restore prior behavior"** — an earlier iteration had it right and a later one
   regressed it — attach the actual prior commit hash and diff (`git show <sha> -- <file>`) as
   ground truth. Asking agy to re-derive it from a description makes it a fresh implementation
   attempt rather than a restore, and that has introduced new bugs the working code never had.
4. **Budget: 3 iterations.** On exhaustion, STOP: set `RECORD.status: blocked`,
   `blocked_reason: budget`, log a `DEC`, and escalate with a crisp summary of what remains. Do not
   quietly take over and write the code yourself.

## Conductor direct edits — narrow exception

The one edit sanctioned by default is fixing a demonstrably **defective test** caught during review
(a wrong or unsatisfiable fixture or assertion) — a planning-artifact correction, and it still
requires a `DEC`.

Direct edits to **application code** are not sanctioned, including one-liners. *"It's trivial,
faster than another agy round"* is still a Role A/B breach: the same actor would have authored,
reviewed, **and** patched the shipped code with no independent check on the patch. If you do it
anyway:

- log the `DEC` **at the moment you make the edit**, not retroactively — state what you changed and
  why agy wasn't asked instead;
- the edit is subject to the same independent G3 review as anything agy produced;
- if the edit turns out to be wrong, that is a **second** `DEC`, also logged the moment you find it
  — never folded silently into the first.

## Safety

The adapter runs agy with `--dangerously-skip-permissions`, which disables **all** of agy's
permission checks — not just file scoping. A delegated run could in principle touch paths outside
the worktree or make network calls. Mitigations: the worktree is throwaway and kept free of
secrets, and every diff is reviewed before it lands. For sensitive repos pass `--sandbox` (verify
the test command still runs under it first).

## Output

`brief.md`, `transcript.log`, `result.iterN.json`, and the worktree left in place for `/ag-close`
to merge. **The Conductor owns the merge — agy never merges.**
