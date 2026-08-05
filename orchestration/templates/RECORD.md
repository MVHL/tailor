---
id:      <N>.<M>
type:    record
parent:  <N>
charter: none
slice:   ""                  # C<n>#SL<m> — set if this task came from a charter slice
status:  in-review           # done | blocked | in-review | rejected
blocked_reason: ""
rejection_reason: ""
rejection_stage: ""
conductor: claude-opus-5     # who framed/planned/scheduled
implementer: agy (<model>)   # who wrote the code
started: <UTC ISO8601>
closed:  <UTC ISO8601 | "">
branch:  task/<N>.<M>
feat:    <FEAT# | "">
comp:    []                  # [COMP1, COMP2] touched
acs:     []                  # [AC1, AC2] delivered
realizes: []                 # [AC1, IM2] this run realized
tests:   <pass | fail | n/a>
mr:      <link | "">
step:    S8
score:   0                   # DERIVED — never hand-set
# ── metrics ── see templates/scoring.md. The board DERIVES every score from these counts
#    plus the artifact graph. Record the raw numbers honestly and the scores follow.
metrics:
  # per-step process analytics (NOT part of the output score)
  frame:    { grill_rounds: 0, acs: 0, reframes: 0 }
  plan:     { tests_planned: 0, red_captured: false }
  delegate: { iterations: 0, agy_turns: 0, timeouts: 0, tokens: 0, seconds: 0 }
  # per-gate — `attributed` maps each finding to the STEP that produced the defect
  gates:
    g1: { rounds: 0, findings_raised: 0, findings_waived: 0, attributed: {} }
    g2: { rounds: 0, findings_raised: 0, findings_waived: 0, attributed: {} }
    g3: { rounds: 0, findings_raised: 0, findings_waived: 0, attributed: {},
          ac_good: 0, ac_flagged: 0, ac_overdue: 0, security_findings: 0 }
  # human cost — is the automation claim actually holding?
  human:    { touches: 0, hg1_latency_h: 0, hg2_latency_h: 0,
              interrupts: [], assumptions_waived: 0 }
  # autonomy — HG1 self-approval, off by default
  autonomy: { auto_approved: false, auto_approval_conditions: [], auto_approval_failed: false }
  # optional — override a derived output dimension when judgement beats arithmetic.
  # Keys: acceptance | tests | defects | security | risk | followups
  # quality: { followups: 90 }
---

# RECORD — <N>.<M>: <title>

## What shipped

<1–3 sentences: what changed and where. Link the diff / MR.>

## Spec delivered

- Problem: `<N>#P1` — <one line>
- Requirements: <R# …>   ·   Non-Goals: <NG# …>
- Acceptance criteria: <AC# — pass/fail each>
- [story-<N>.<M>.md](./story-<N>.<M>.md) · [TP.md](./TP.md) · [IP.md](./IP.md)
- Gates: [G1](./review-framing.md) · [G2](./review-readiness.md) · [G3](./review-code.md)
- [transcript.log](./transcript.log) · [decisions.md](./decisions.md)

## Verification

- Tests: `<command>` → <result; note red→green explicitly>
- G3 verdict: <pass; summary> — <n> findings, <n> waived

## Charter feedback

*(Only when `slice:` is set. This is appended to the charter's bet log by `/ag-close`.)*

- **Slice:** `C<n>#SL<m>`
- **Did the thesis hold?** <yes / partly / no — with the evidence>
- **Recommendation:** <continue / reorder / cut SL# / re-bet>

<!-- ── REQUIRED CLOSING SECTIONS — never omit. Write "None." if empty. ──
     The first two are ROLL-UPS of open annotations (WORKFLOW §12), not fresh prose:
     do not invent items here that don't exist as ASM/OQ in the artifacts.        -->

## Assumptions

*Roll-up of `ASM` still `open` at close.*

- `ASM#` <text>   `affects: <item>`   — <why it was never resolved>

## Open issues

*Roll-up of `OQ` still `open` at close. Feeds the `followups` output dimension.*

- `OQ#` <text>   `affects: <item>`   — <deferral target, or the NG it became>

## Discovered problems

*Findings about reality, outside this task's scope. Each one is **mintable as a new `SIG`** —
say whether it was.*

- <problem>   → `minted as: <container-id>` | `not minted: <why>`

## Possible bugs

*Suspected but unconfirmed defects.*

- <suspected defect> — how to reproduce or confirm
