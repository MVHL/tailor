---
name: ag-review-framing
description: Gate G1 — grade the framing artifacts (SIG/ASK/P/R/NG/AC) as an independent cold assessor that has not seen the grill, raising itemized findings attributed to the step that produced them, and loop until pass. Run after ag-frame and before any planning. Use when asked to "review the framing", "check the spec", or run the G1 gate.
---

# ag-review-framing — G1

You are **Role B (Assessor)**. This gate exists because the author is the wrong judge of their own
framing. Read `WORKFLOW.md` §5 (gate contract) and §6 (artifact registry) first.

## The independence rule — non-negotiable

> **Run the judgment pass in a fresh sub-agent that has NOT seen the grill.**

Spawn it with the `Agent` tool and hand it **only** the artifact files. Do not summarize the
framing rationale for it, do not tell it what the author intended, do not tell it what you expect
to find. A reviewer who saw the grill rationalizes instead of assessing — that failure is silent
and it is the whole reason this is a separate gate rather than a section of `ag-frame`.

## Inputs

The spec-chain documents for the item, and nothing else:
`prp-<n>.md`, `prd-<n>.md` (if full form), `spike-<n>.md` (if any), and each
`story-<n>.<m>.md` produced at S4.

## Scope — quality, never worth

A gate never rejects an item. It says *"this spec is broken"*, never *"this shouldn't be built"*.
If the review concludes the work isn't worth doing, raise it as an `OQ` and route it to **HG1** —
that is a human decision (`WORKFLOW` R9).

## Checks

Run each as a **ratio** (share of items passing), not a boolean — the score must degrade in
proportion to how much is broken.

**Intake**
- every `SIG` has `source:` + `date:` and reads as verbatim evidence, not a paraphrase
- every `ASK` links ≥1 `SIG`, and is labelled a hypothesis rather than a requirement
- no `ASK` text has been copied into an `R`

**Problem**
- every `P` cites `evidence: SIG#/ASK#` — **a `P` with no signal is an invented need**
- every `P` states who is affected and the impact, with a metric
- every `P` has ≥1 `R` or `NG` — a problem with neither is untriaged
- `discovery_coverage` = 1.0 (answered · assumed · `n/a`+reason); each blank aspect is a finding
  **attributed to S2**

**Scope**
- no orphan `R` — every `solves:` **resolves**, locally or as `<container>#<tag>`
- every `R` is covered by ≥1 `AC`
- every `NG` carries **`excludes: P#`** and a deferral target — the unsolved share of each problem
  must be explicit, not implied
- ≥1 `NG` exists (scope is bounded)
- `D`/`RK` from a spike are **visibly factored** into `R`/`NG`

**Acceptance criteria**
- every `AC` has `covers: R#` and is **observable and testable** — a clear pass/fail, not a
  judgment. Rewrite requests here are findings, not suggestions.
- every canonical `AC` sits in a story, not only in the PRD

**Structure**
- the item's form matches the §7 threshold — a collapsed item that exceeded it is a finding
- a referenced `P` has a read-only copy embedded next to the pointer
- inherited charter constraints are present when `charter:` is set

**Annotations**
- every `ASM` and `OQ` has `affects:` and a `state:`
- **no `ASM` on scope aspect 5 or 6** — that blocks HG1, and shipping it past this gate is a defect

## Findings

Write `review-framing.md` from `templates/review.md`:

- one **verdict per input artifact**, never one for the bundle;
- each finding as `F<n>` with `severity`, **`attributed-to: S<step>`** — the step that *produced*
  the defect, not the one that found it — `resolution`, and the evidence in the artifact.

`attributed-to` is the field that makes a step independently improvable. *"G1 raised 14 findings
across 6 epics, 11 against Discovery"* is actionable; a bare count is not.

## The loop — budget 3 rounds

1. Report findings to the author (`ag-frame`), which fixes and re-runs this gate.
2. A finding closes as **fixed** or **waived with a `DEC`** — never "ignored". You may waive your
   own G1 findings; record why it cannot be fixed now. Waivers are counted and deduct from the
   artifact score.
3. On exhaustion: stop, set the artifact `status: blocked`, log a `DEC`, escalate with a crisp
   summary of what remains. Do not pass a broken spec to keep the loop moving.

## On pass

Set the reviewed artifacts to `status: canonical`, write the verdict, and report the next step —
`/ag-test-plan <id>` (S5). Note the framing score contribution and any waived findings so the
number stays explainable.
