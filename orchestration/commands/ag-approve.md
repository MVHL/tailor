---
description: HG1 — present the scope triple (P + R + NG) with the discovery-coverage report and open assumptions, and record the human's scope approval.
argument-hint: "<container-id>"
---

Human scope approval for **$ARGUMENTS**. This is `WORKFLOW.md` **HG1** — placed before S4 so no
slicing, test planning, or delegation is spent on unapproved scope.

## 1. Check it is presentable

Run the S3 exit check first (mechanical, cheap): no orphan `R`, every `R` has ≥1 `AC`, every `NG`
carries `excludes: P#` and a deferral target, ≥1 `NG` recorded. If any fail, fix them before
spending the human's attention — do not ask them to approve a spec that is internally broken.

## 2. Present exactly this

- **The scope triple** — `P` + `R` + `NG`. **This is what is being approved.**
- **`discovery_coverage`** as a fraction, **with the open-assumption count next to it.** Coverage
  measures *considered*, not *known*: 1.0 with six assumptions is well-surveyed, not
  well-understood.
- **Every open `ASM`**, as a batch to resolve now. This is the point of batching — the human answers
  a list once instead of being interrupted throughout the grill.
- **Draft `AC`** — *shown* so `R` is concrete, but **not** what is being approved. Testability is a
  mechanical judgment made at G1/G2, not a human one.
- Any `OQ` that a scope decision would settle.

**Blocking condition:** an `ASM` on scope aspect **5** (which parts of `P` are solved vs. not) or
**6** (each `NG`'s deferral target) **blocks approval**. You cannot approve scope that is itself
assumed — resolve those first, and say so rather than presenting anyway.

## 3. Record it

On approval, in `prd-<n>.md` (or the collapsed doc):

- `status: canonical`, `approved_by: <name>`, `approved_at: <UTC ISO8601>`;
- fill the **Scope approval** section: coverage at approval, open-assumption count, and which `ASM`
  were **accepted at the gate**;
- log a `DEC` at **epic** level with `Kind: approval`, linking `accepts: ASM#` for each.

An approval that leaves no record is not an approval — the board cannot show "waiting on human" and
nobody can audit who said yes to the scope.

## Rejection is a valid outcome here

If the human decides it is real but not worth it now: `status: rejected`,
`rejection_reason: not-now`, `rejection_stage: HG1`. It **must** become an `NG` on the parent (or a
`BND` on the charter) **with a deferral target** — otherwise scope silently vanishes while looking
rigorous. Log the `DEC`. A rejected `P` does **not** invalidate its `SIG`: move the signal to the
unaddressed pool in `graph.md`.

## Self-approval

Permitted **only** when all five hold *and* this repo has an enabling `DEC` (default: off):
collapsed form · `discovery_coverage` 1.0 with **zero** assumptions · no `D`/`RK`/rejection
proposed · the `SIG` is **machine-generated** (stack trace, failing test, alert — not a human ask) ·
no new `COMP` and no new glossary term.

Log it as a `DEC` with `Decided by: Conductor (auto)` **listing the five conditions met**. If any
condition is uncertain, ask the human — the conditions are deliberately narrow, and the only
objectively checkable one is the machine-generated `SIG`.

Report: approved or not, what was accepted, and the next step (`/ag <id>` → S4).
