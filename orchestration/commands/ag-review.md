---
description: G3 — the code review gate. Objective checks (tests, diff, gamed-test detection) then an independent sub-agent grades each AC. Loops with agy up to the iteration budget; blocks the merge.
argument-hint: "<container-id>"
---

Run gate **G3** on **$ARGUMENTS**. Invoke the **ag-review-code** skill.

> **The git diff and the test run are the source of truth. agy's self-report is never trusted.**

## Part 1 — objective checks (you run these; mechanical, not judgment)

In `.orchestration/worktrees/<id>`:

1. **Run the `TP` tests.** Capture pass/fail and note **red→green** explicitly. Necessary but *not
   sufficient* — green proves the suite ran, not that it measured real behavior.
2. **Read the whole diff** (`git -C <worktree> diff HEAD`). Were tests edited, weakened, skipped, or
   deleted to pass? **If so, reject the iteration outright** — not a finding to negotiate.
3. **Check for gamed tests that were never edited.** A green suite can still be satisfied by
   fabricated output rather than real logic, with **no test file touched at all** — e.g. a
   diff/highlight/transform test that only checks structural presence or an element count, satisfied
   by an invisible dummy marker instead of a genuine computation. For any test verifying a visual or
   content transformation, confirm the assertion is satisfied by **real logic against the literal
   fixture data**, not merely that something of the right shape exists. This is the same cheating risk
   as check 2 with no diff evidence to make it visible — which is why it must be looked for.
4. **Does the diff realize `IP.md`?** Unplanned scope in the diff is a finding, not a bonus.
5. Commits reference the realized ids.

Test-cheating is a **hard fail**: record it under *Discovered problems* and set
`metrics.quality.tests: 0`. Do not soften it to "flagged".

## Part 2 — independent judgment

**Spawn a fresh sub-agent** and hand it only the diff, the story, and `TP.md` — **not** the framing
rationale. Have it run the `review` skill (standards + spec), plus `security-review` on risky changes,
and **explicitly ask it to look for check-3-style gamed tests**: it reads the implementation without
the authoring context biasing it toward "this looks right".

Then **grade each `AC`** — good (passing test + clean impl) / flagged (works but issues) / overdue
(not done), per the `ticket-execution-review` model. **Prefer the sub-agent's grades** over your own;
they feed `metrics.gates.g3` directly.

## Findings and waivers

Write `review-code.md` from `templates/review.md`: verdict per artifact, findings as `F<n>` with
`severity`, **`attributed-to: S<step>`**, `resolution`, evidence.

Attribute honestly: a finding whose real cause is a vague `AC` belongs to **S3/S4**, not S7. Blaming
the implementer for a planning defect is how a broken upstream step stays broken.

**You may NOT waive** a `blocker`/`high` finding or **any** security finding at G3 — those require the
human at HG2. Otherwise the same actor raises, waives, and ships the finding.

## Loop and exit

Any `AC` not **good** → hand the fix instruction to `/ag-delegate <id> --iterate`. **Budget: 3.** On
exhaustion: `status: blocked`, `blocked_reason: budget`, log a `DEC`, escalate.

**Pass only when:** every `AC` has a passing test with red→green observed; the diff realizes the `IP`
with nothing unplanned; no test was weakened and no gamed-but-untouched test survives check 3; review
is clean or every remaining finding is low/medium and waived with a `DEC`.

On pass: append the real `touches:` anchors to `IP.md` and `graph.md`, set `verdict: pass`, and report
**HG2** — the human's merge approval, via `/ag-close <id>`. **Do not merge here.**
