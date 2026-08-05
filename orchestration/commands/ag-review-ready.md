---
description: G2 — the Definition-of-Ready gate. An independent assessor checks TP and IP against the AC (coverage, real red state, non-vacuous tests, reuse, inherited constraints) and loops until pass. Blocks delegation.
argument-hint: "<container-id>"
---

Run gate **G2** on **$ARGUMENTS**. Invoke the **ag-review-ready** skill.

**Spawn a fresh sub-agent** for the judgment pass, handed only `story-<n>.<m>.md`, `TP.md`, `IP.md`,
the captured red output, and the charter constraints if any. Do not tell it what the planner intended
or which parts they were unsure about.

Checks:

- **Coverage (the core of DoR)** — every `AC` has ≥1 `T` **and** ≥1 `IM`; no orphan `IM`; no `T`/`IM`
  pointing at an `AC` that doesn't exist; no `AC` left unplanned.
- **Test Plan** — `red_captured` is **real** (verify the pasted output is genuine failing output from
  the named command, don't trust the flag); exactly one run command that actually runs the listed
  tests; happy/edge/error per `AC` or a stated reason; **non-vacuity holds** for each test; the test
  files exist in the worktree and are on the task branch.
- **Impl Plan** — the approach names the seam and what must not cross it; the reuse list is non-empty
  or explicitly justified; **inherited charter constraints are cited**, not merely inherited;
  guardrails present; `IM` sequenced for incremental green.
- **Consistency** — the `AC` here match the canonical ones (planning must not have quietly rescoped);
  the referenced parent `P` is not `stale`.
- **Annotations** — any `OQ` that would change the **approach** is resolved, not carried.

An `AC` that proves **untestable at reasonable cost** is a legitimate finding **attributed to
S3/S4** — send it back to be reworded rather than writing a weak test around it.

**Scope: quality, never worth.** G2 does not reject an item; if the plan reveals the work isn't worth
doing, that is an `OQ` routed to HG1.

Write `review-readiness.md` from `templates/review.md` — a verdict per artifact, findings as `F<n>`
with `severity` and **`attributed-to`**.

**Loop: 2 rounds** (the author is fixing their own plan; a third round means it needs re-thinking,
not patching). Findings close as **fixed** or **waived with a `DEC`**. On exhaustion:
`status: blocked`, log a `DEC`, escalate.

On pass: set `TP.md` and `IP.md` `canonical` and report `/ag-delegate <id>` (S7).

**Nothing reaches agy without this gate passing.** If asked to skip it, say no and explain what it
protects — a bad plan is paid for in agy iterations and reviewer attention, both more expensive than
one more round here.
