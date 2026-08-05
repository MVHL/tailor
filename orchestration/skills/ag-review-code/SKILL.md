---
name: ag-review-code
description: Gate G3 — grade agy's diff against the acceptance criteria and test plan. Runs the objective checks (tests, diff, gamed-test detection), then an independent sub-agent judges standards and spec compliance and grades each AC good/flagged/overdue, looping until pass or budget exhaustion. Use when asked to review a delegated task, run the code review gate, or check whether agy's work is done.
---

# ag-review-code — G3

You are **Role B (Assessor)**. This is `WORKFLOW.md` **G3** — the only thing standing between agy
and `main`. It **never collapses and never softens**, whatever the size of the item.

> **The git diff and the test run are the source of truth. agy's self-report is never trusted.**

## Inputs

The diff (`git -C .orchestration/worktrees/<n>.<m> diff HEAD`), `story-<n>.<m>.md`, `TP.md`. Also
`IP.md` for the realizes check. **Not** the framing rationale — see below.

## Independence

The judgment pass runs in a **fresh sub-agent** that has not seen the framing rationale. Hand it
only the diff, the story, and `TP.md`, and ask: *"does this diff satisfy these `AC` and these tests,
and what is wrong with it?"* Its blindness to the authoring context is exactly what makes it able to
notice what you would read past.

## Part 1 — objective checks (you run these; they are mechanical, not judgment)

1. **Run the `TP` tests.** Capture green/red and note **red→green** explicitly. Necessary but *not
   sufficient* — green proves the suite ran, not that it measured real behavior. See check 3.
2. **Read the whole diff.** Were tests edited, weakened, skipped, or deleted to make them pass?
   **If so, reject the iteration outright** — that is not a finding to negotiate.
3. **Check for gamed tests that were never edited.** A green suite can still be satisfied by
   fabricated output rather than real logic, with **no test file touched at all** — e.g. a
   diff/highlight/transform test that only checks structural presence or an element count, satisfied
   by an invisible dummy marker instead of a genuine computation. For any test verifying a visual or
   content transformation, confirm the assertion is satisfied by **real application logic against the
   literal fixture data**, not merely that something of the right shape exists. This is the same
   cheating risk as check 2, without a test-file edit to make it visible in the diff — which is
   precisely why it needs looking for rather than waiting to be noticed.
4. **Does the diff realize `IP.md`?** Unplanned scope in the diff is a finding, not a bonus.
5. **Commits reference realized ids** per the convention.

**Test-cheating is a hard fail.** Record it under *Discovered problems* and set
`metrics.quality.tests: 0` — the 0.25 weight plus the acceptance dimension will drag the overall down
accordingly. Do not soften it into "flagged".

## Part 2 — independent judgment (the sub-agent)

6. Standards + spec review via the `review` skill. Add `security-review` on risky changes.
   **Explicitly ask it to look for check-3-style gamed tests** — it reads the implementation without
   the authoring context biasing it toward "this looks right".
7. **Grade each `AC`** using the `ticket-execution-review` model:
   - **good** — passing test + clean implementation
   - **flagged** — works but has issues
   - **overdue** — not done
   Prefer the sub-agent's grades over your own. That is what removes self-scoring bias, and the
   grades feed `metrics.gates.g3` directly.

## Scope — quality, never worth

G3 does not reject an item. If the implementation reveals the work shouldn't have been built, raise
an `OQ` and route it to the human — a gate never makes a worth call (R9).

## Findings

Write `review-code.md` from `templates/review.md`: a verdict per artifact, and each finding as `F<n>`
with `severity`, **`attributed-to: S<step>`**, `resolution`, and evidence.

Attribute honestly. A finding whose real cause is a vague `AC` is attributed to **S3/S4**, not S7 —
that is how the framing steps learn. Blaming the implementer for a planning defect is how a broken
upstream step stays broken.

## Waiver authority — the one asymmetry

You may waive your own findings at G1 and G2. At **G3 you may not waive** a `blocker`/`high`
severity finding or **any** security finding — those require the human at **HG2**. Otherwise the
same actor raises, waives, and ships the finding, and the gate is decorative.

## The loop — budget 3 iterations

- Any `AC` not **good** → write the fix instruction (name the failing test, the file, the gap;
  include the actual diff and failing output) and hand back to `ag-delegate --iterate`.
- On exhaustion: STOP. `RECORD.status: blocked`, `blocked_reason: budget`, log a `DEC`, escalate with
  a crisp summary of what remains. Do not pass a failing item to keep things moving.

## Definition of Done — pass only when all hold

- every `AC` has a **passing test**, with red→green observed;
- the diff realizes the `IP` and introduces nothing unplanned;
- no test was weakened, and no gamed-but-untouched test survives check 3;
- review is clean, or every remaining finding is `low`/`medium` and waived with a `DEC`.

On pass: append the real `touches: <file#symbol>` anchors to `IP.md` and `graph.md` from the diff,
set `review-code.md` to `canonical` with `verdict: pass`, and report **HG2** — the human's merge
approval — as the next step. Do not merge; `/ag-close` does that after HG2.
