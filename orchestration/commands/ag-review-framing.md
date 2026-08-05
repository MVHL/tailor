---
description: G1 — independent cold assessor grades the framing artifacts (SIG/ASK/P/R/NG/AC), raises findings attributed to the step that caused them, and loops until pass. Blocks planning.
argument-hint: "<container-id>"
---

Run gate **G1** on **$ARGUMENTS**. Invoke the **ag-review-framing** skill.

**Spawn a fresh sub-agent for the judgment pass** and hand it **only** the artifact files —
`prp-<n>.md`, `prd-<n>.md`, `spike-<n>.md`, and each `story-<n>.<m>.md`. Do not summarize the grill
for it, do not say what the author intended, do not hint at what you expect it to find. A reviewer
that saw the framing rationalizes instead of assessing, and that failure is silent.

Checks (each a **ratio**, never a boolean):

- **Intake** — `SIG` verbatim with source + date; every `ASK` links a `SIG` and is labelled a
  hypothesis; no `ASK` text copied into an `R`.
- **Problem** — every `P` cites `evidence:`; states who is affected + impact with a metric; has ≥1
  `R` or `NG`; `discovery_coverage` = 1.0 (each blank aspect is a finding **attributed to S2**).
- **Scope** — no orphan `R` (every `solves:` **resolves**); every `R` has ≥1 `AC`; every `NG` has
  **`excludes: P#`** + a deferral target; ≥1 `NG`; `D`/`RK` visibly factored into `R`/`NG`.
- **AC** — `covers: R#`, and **observable + testable** (a clear pass/fail, not a judgment); canonical
  `AC` live in a story, not only in the PRD.
- **Structure** — the form matches the §7 threshold; a referenced `P` has its read-only copy embedded;
  inherited charter constraints present when `charter:` is set.
- **Annotations** — every `ASM`/`OQ` has `affects:` and `state:`; **no `ASM` on scope aspect 5 or 6**.

Write `review-framing.md` from `templates/review.md`: **one verdict per input artifact** (never one
for the bundle), and each finding as `F<n>` with `severity`, **`attributed-to: S<step>`** — the step
that *produced* the defect, not the one that found it — `resolution`, and evidence.

**Scope: quality, never worth.** A gate says *"this spec is broken"*, never *"this shouldn't be
built"*. If the review concludes the work isn't worthwhile, raise an `OQ` and route it to HG1.

**Loop: 3 rounds.** Findings close as **fixed** or **waived with a `DEC`** — never ignored. You may
waive your own G1 findings; waivers are counted and deduct from the artifact score. On exhaustion:
`status: blocked`, log a `DEC`, escalate with what remains. Do not pass a broken spec to keep things
moving.

On pass: set the reviewed artifacts `canonical` and report `/ag-test-plan <id>` (S5), the framing
score contribution, and any waived findings so the number stays explainable.
