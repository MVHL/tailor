---
id:      <N>.<M>            # task-level ids are ALWAYS dotted, even when there is only one
type:    story              # story | bug | tech
parent:  <N>                # the container that owns the P — or `none` if collapsed here
charter: none
slice:   ""
form:    full               # full | collapsed (collapsed = SIG…AC all live in this one file)
status:  draft              # draft → canonical (at G1) → consumed (at S7) | rejected
blocked_reason: ""
rejection_reason: ""
rejection_stage: ""
approved_by: ""
approved_at: ""
step:    S4
inputs:  [<N>#R1, <N>#NG1]
score:   0                  # DERIVED
jira:    ""
---

# <STORY|BUG|TECH> <N>.<M> — <title>

The task-level deliverable. Holds the `R`/`NG` **subset** sliced from the PRD, plus the
**canonical** `AC`. This is what `TP.md`, `IP.md`, and agy's brief are built from.

## Problem (read-only — canonical in `<N>`)

> **`<N>#P1`** — <verbatim copy of the parent problem statement>

The copy is a **cache** for agy's brief and for the cold assessor; the pointer is truth. If the
parent `P` changes, this document goes `stale` and must be re-blessed.

*(Collapsed form: delete the quote above, own the `P` locally, and paste the `SIG`/`ASK`/`P`
sections from `templates/prp.md` here — including the Discovery-coverage table.)*

## Requirements in this slice — `R`

- **R1** <outcome>   `solves: <N>#P1`   `part-of: FEAT1`

## Non-Goals in this slice — `NG`

- **NG1** <excluded>   `excludes: <N>#P1`   `deferred to: <ref>`

## Acceptance criteria — `AC` (canonical)

Every `AC` must be **observable and testable** — a clear pass/fail, not a judgment. Every `R`
in this slice needs at least one.

- **AC1** <condition>   `covers: R1`   `in: COMP1`
- **AC2** <condition — the edge or error case>   `covers: R1`   `in: COMP1`

## Inherited charter constraints

*(Only when `charter:` is set. `IP.md` must cite these explicitly — G2 checks it.)*

- <cross-cutting constraint copied from `charter-C<n>.md`>

## Assumptions — `ASM`

- **ASM1** <taken as true>   `affects: AC1`   `state: open`

## Open questions — `OQ`

- **OQ1** <would change the work>   `affects: AC1`   `state: open`

## Tags

`FEAT:` <FEAT#>   ·   `COMP:` <COMP#…>
