---
id:      <N>                # container id — epics and standalone items share one counter
type:    prp
parent:  none
charter: none               # C<n> if this was minted from a slice — MUTABLE
slice:   ""                 # C<n>#SL<m> it was minted from, if any
form:    full               # full | collapsed  (collapsed = this file also holds R/NG/AC)
status:  draft              # draft → canonical (at G1) → consumed (at S3/S4) | rejected
blocked_reason: ""
rejection_reason: ""        # dissolved|infeasible|not-now|duplicate|superseded
rejection_stage: ""         # S2|S2b|HG1
approved_by: ""             # set at HG1 (the scope triple)
approved_at: ""
discovery_coverage: 0       # answered / (11 − n/a) — see the checklist below
step:    S1
inputs:  []
score:   0                  # DERIVED
jira:    ""
---

# PRP <N> — <title>

Intake and problem framing. `SIG` and `ASK` are captured at **S1**; `P` is drafted at S1 and
sharpened at **S2** (Discovery). `R`/`NG`/`AC` do **not** live here in `full` form — they go to
`prd-<N>.md` at S3. In `collapsed` form they are appended below.

## Signals — `SIG` (verbatim, never paraphrased)

- **SIG1:** "<the exact words / error output / quote>"   `source: <where>`   `date: <YYYY-MM-DD>`

> A machine-generated `SIG` (stack trace, failing test, monitoring alert) is the strongest
> evidence there is — and the only kind that permits HG1 self-approval (see WORKFLOW §5).

## Asks — `ASK` (a solution hypothesis, NOT a requirement)

- **ASK1:** <what was literally asked for>   `distilled from: SIG1`

> Never copy an `ASK` into a requirement. An ask with no signal is unfounded — carry it as an
> `ASM` to test.

## Problems — `P`

- **P1:** <who> <pain> — <impact, with a metric>   `evidence: SIG1, ASK1`

> A problem with no signal is an **invented need**. Challenge it or drop it.
> If this PRP was minted from a charter slice, `evidence:` may cite `C<n>#ASK1` as *context*,
> but at least one local `SIG` is still required.

## Discovery coverage (the S2 exit check)

Mark each `answered` · `assumed` (open an `ASM`) · `n/a + reason`. Blank is a G1 finding.
Reported to the human at HG1 — see the guard note below.

| # | Aspect | State | Note |
|---|--------|-------|------|
| 1 | Who is affected — role + rough count | | |
| 2 | Frequency — how often it bites | | |
| 3 | Impact — cost of doing nothing, with a metric | | |
| 4 | Current workaround — what they do today instead | | |
| 5 | **Scope split** — which parts of `P` are solved (`R`) and which are not (`NG`) | | |
| 6 | **Deferral target** for each `NG` | | |
| 7 | Constraints — perf, compat, security, data, deadline | | |
| 8 | Invariants — what must stay true that nobody said out loud | | |
| 9 | Edge cases and failure modes at the boundaries | | |
| 10 | Dependencies and risks — external actors, what could undermine this | | |
| 11 | How we will know it worked — the observable signal | | |

`discovery_coverage` = `answered / (11 − n/a)`. **Coverage measures *considered*, not *known*** —
an `assumed` aspect counts, so report the assumption count next to it.

> **Guard:** an `ASM` on aspect **5** or **6** *blocks HG1*. You cannot approve scope that is
> itself assumed. Assumptions elsewhere may pass the gate.

## Assumptions — `ASM`

- **ASM1** <taken as true without evidence>   `affects: P1`   `state: open`

## Open questions — `OQ`

- **OQ1** <a question whose answer would change the work>   `affects: P1`   `state: open`

> `OQ` answered → becomes a `DEC`. `OQ` unanswerable now → downgrade to an `ASM` so work
> proceeds explicitly rather than silently.

## Tags

`FEAT:` <FEAT# — grouping>   ·   `COMP:` <COMP# — bounded context(s)>

<!-- ─────────────────────────────────────────────────────────────────────────
     COLLAPSED FORM ONLY (form: collapsed) — below the §7 threshold:
       1 P · ≤3 R · ≤5 AC · no D · no RK · one COMP
     Append R / NG / AC here instead of creating prd-<N>.md. If any threshold
     breaks, split into prd-<N>.md + story-<N>.<M>.md, keeping this id.
     ───────────────────────────────────────────────────────────────────────── -->

## Requirements — `R`   *(collapsed form only)*

- **R1** <outcome that must be true>   `solves: P1`   `part-of: FEAT1`

## Non-Goals — `NG`   *(collapsed form only)*

- **NG1** <excluded scope>   `excludes: P1`   `deferred to: <ref>`

> `excludes: P#` is **required** — the unsolved share of each problem must be explicit, not
> implied. That is what makes "how much of the problem are we solving" answerable.

## Acceptance criteria — `AC`   *(collapsed form only)*

- **AC1** <observable, testable pass/fail condition>   `covers: R1`   `in: COMP1`
