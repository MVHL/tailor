---
description: HG2 + S8 — ask for the merge go, then write the RECORD, update graph/index, merge the worktree, append to the charter bet log, and schedule what's next.
argument-hint: "<container-id>"
---

Close **$ARGUMENTS**. Only proceed if `review-code.md` has `verdict: pass` — otherwise say why and
stop.

## 1. HG2 — the merge approval (human)

Merging to the default branch is **irreversible and outward-facing**, and it is the one point where an
automated decision reaches `main`. Present:

- what shipped, and the `AC` grades;
- every **waived** finding, especially any the Conductor could not waive itself;
- the test result with red→green confirmed.

Then **ask for the go and wait.** Delegable *only* if this repo has a standing `DEC` enabling
auto-merge (e.g. *"auto-merge when G3 passes with no high-severity and no security finding"*) — never
by per-item confidence. Log the approval as a `DEC` with `Kind: approval` at task level.

## 2. RECORD

Write `runs/<id>/RECORD.md` from `templates/RECORD.md`. Fill the frontmatter (`status: done`,
`branch`, `acs`, `realizes`, `comp`, `tests`, timestamps, `slice:` if applicable) and the body.

The four closing sections are **mandatory** — write "None." where empty. The first two are
**roll-ups**, not fresh prose:

- **Assumptions** — every `ASM` still `open`, with why it was never resolved;
- **Open issues** — every `OQ` still `open` (feeds the `followups` dimension);
- **Discovered problems** — out-of-scope findings; say for each whether it was **minted as a new
  `SIG`** or why not;
- **Possible bugs** — suspected, unconfirmed, with how to reproduce.

Do not invent items here that don't exist as `ASM`/`OQ` in the artifacts, and do not quietly drop ones
that do.

## 3. Metrics

Fill the `metrics` block honestly per `templates/scoring.md`. Sum `.num_turns`,
`.usage.total_tokens`, `.duration_seconds` across `result.iter*.json`. Record each gate's `rounds`,
`findings_raised`, `findings_waived`, and **`attributed`** map; the human costs (`touches`, approval
latencies, `interrupts`, `assumptions_waived`); and the autonomy flags.

**Do not hand-write scores** — the board derives them. A low score is signal, not a failure to
massage.

## 4. Graph and index

Update `.orchestration/graph.md`: the run row, `touches:` anchors from the diff, new `FEAT`/`COMP`,
`DEC` rows, any **stale watch** entries, and — if something was rejected — the rejected and
unaddressed-signal tables. Append a row to `runs/index.md`.

## 5. Merge (you own it — agy never merges)

Merge `task/<id>` into the working branch, **re-run the tests on the merged result**, then
`git worktree remove --force .orchestration/worktrees/<id>` (`--force` because build byproducts like
`__pycache__` are expected there; the code is already merged) and `git worktree prune`.

## 6. Charter feedback

If `slice:` is set, **append to the charter's bet log**: what shipped, did the thesis hold, and a
recommendation. Set the `SL` `state: done`. Without this hook the charter is a fan-out with no
feedback.

## 7. Schedule what's next (S8 is the scheduler)

1. If `review_after` has been **reached** → **halt** and request the re-bet (`/ag-charter <C> --review`).
   **Do not mint past a due re-bet.**
2. Else compute the **mintable set** — every `SL` whose `needs:` are closed; and until `UNK1` is
   reduced, only `SL1` counts — and mint the next slice (`/ag-charter <C> --mint <SL#>`). v1 mints
   **one at a time**.
3. If the charter has no slices left → report it complete.
4. If the item was standalone → report done; no further action.

## 8. Commit

Commit the run directory + graph + index. Show the diff and confirm before committing anything
destructive.

Report: what shipped, the four closing-section highlights, the derived scores, the record path, and
the next action you scheduled (or the re-bet you are waiting on).
