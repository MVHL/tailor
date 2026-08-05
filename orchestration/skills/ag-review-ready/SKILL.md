---
name: ag-review-ready
description: Gate G2 — the Definition-of-Ready review. An independent assessor checks the Test Plan and Impl Plan against the acceptance criteria (coverage, captured red state, non-vacuous tests, reuse, inherited constraints) and loops until pass. Run after the impl plan and before delegating to agy. Use when asked to run the readiness gate, check DoR, or verify a task is ready to delegate.
---

# ag-review-ready — G2 (Definition of Ready)

You are **Role B (Assessor)**. This gate is what makes delegation safe: it is the last check before
tokens are spent on implementation. Read `WORKFLOW.md` §5 and §6 first.

It exists as a separate gate — rather than a section of `ag-impl-plan` — because the planner
blessing their own plan is the same Role A/B breach the contract forbids everywhere else.

## Independence

Spawn a fresh sub-agent for the judgment pass, handed **only** the artifacts below. It should not
be told what the plan's author intended or which parts they were unsure about.

## Inputs

`story-<n>.<m>.md` (canonical `AC`), `TP.md`, `IP.md`, the captured red output, and the charter's
cross-cutting constraints if `charter:` is set. Not the framing conversation.

## Checks

**Coverage — the core of DoR**
- every `AC` has ≥1 `T` (`covers: AC#`) **and** ≥1 `IM` (`implements: AC#`)
- no orphan `IM` (an `IM` with no `implements:`)
- no `AC` left unplanned, and no `T`/`IM` pointing at an `AC` that doesn't exist

**Test Plan**
- **`red_captured` is real** — the pasted output is genuine failing output from the named command,
  not a placeholder. A green suite with no captured red state is scored as if the tests might be
  vacuous, so verify this rather than trusting the flag.
- exactly **one** run command, and it actually runs the listed tests
- happy / edge / error present per `AC`, or an explicit reason one is inapplicable
- **non-vacuity**: for each `T`, the stated reason it cannot pass without the feature holds up.
  A test satisfied by the unmodified codebase is worthless — catching that here costs one round;
  catching it at G3 costs a delegation.
- the tests exist as **real files** in the worktree and are on the task branch

**Impl Plan**
- the approach names the seam (`COMP#`) and what must not cross it
- the reuse list is non-empty, or its emptiness is explicitly justified — a silently empty list
  usually means nobody looked
- **inherited charter constraints are cited**, not merely inherited (`WORKFLOW` §4)
- guardrails present: what not to touch, commit convention, no test weakening, no merge/push
- `IM` steps are sequenced so tests can go green incrementally

**Consistency with the blessed spec**
- the `AC` here match the canonical ones — planning must not have quietly rescoped
- referenced parent `P` is not `stale`

**Annotations**
- any `OQ` that would change the **approach** is resolved, not carried. One that changes only a
  detail may be downgraded to an `ASM` — but it must say which, explicitly.

## Scope — quality, never worth

G2 does not reject an item. If the plan reveals the work isn't worth doing, that is an `OQ` routed
to HG1, not a gate failure.

An `AC` that turns out to be **untestable at reasonable cost** is a legitimate G2 finding
**attributed to S3/S4** — send it back to be reworded rather than writing a weak test around it.

## Findings and the loop — budget 2 rounds

Write `review-readiness.md` from `templates/review.md`: a verdict per artifact, findings as `F<n>`
with `severity` and **`attributed-to`**. Two rounds, because the author is fixing their own plan
and a third round means the plan needs re-thinking rather than patching.

Findings close as **fixed** or **waived with a `DEC`**. On exhaustion: `status: blocked`, log a
`DEC`, escalate.

## On pass

Set `TP.md` and `IP.md` to `canonical`, and report `/ag-delegate <id>` as the next step. State the
framing-score contribution and any waivers.

**Nothing reaches agy without this gate passing.** If asked to skip it, say no and explain what it
protects: the cost of a bad plan is paid in agy iterations and reviewer attention, both of which
are more expensive than one more round here.
