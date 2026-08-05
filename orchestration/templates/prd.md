---
id:      <N>
type:    prd
parent:  none
charter: none
slice:   ""
status:  draft              # draft → canonical (S3 exit check + HG1) → consumed (at S4)
blocked_reason: ""
rejection_reason: ""
rejection_stage: ""
approved_by: ""             # set at HG1 — the scope triple P + R + NG
approved_at: ""
step:    S3
inputs:  [<N>#P1]           # the canonical items this was built from
score:   0                  # DERIVED
jira:    ""
---

# PRD <N> — <title>

Epic-level scope. `R` and `NG` become **canonical** here; `AC` is only **drafted** here and
becomes canonical when sliced into a story at S4.

Problem source: [prp-<N>.md](./prp-<N>.md) — `P` is **not** re-authored here.
Spike findings, if any: [spike-<N>.md](./spike-<N>.md).

## Problems in scope (reference — canonical in the PRP)

- `<N>#P1` — <one line, for the reader's benefit>

## Requirements — `R`

- **R1** <user-facing outcome that must be true>   `solves: <N>#P1`   `part-of: FEAT1`
  - `constrained by: D1` — *(if a spike surfaced a dependency)*

> Every `R` needs a **resolvable** `solves:`. An `R` with no problem is an orphan and fails G1.

## Non-Goals — `NG`

- **NG1** <excluded scope>   `excludes: <N>#P1`   `deferred to: <ref or "not planned">`
  - `justified by: RK1` — *(if a risk is why this is excluded)*

> `excludes: P#` is **required**. `R` says how much of the problem we solve; `NG` says how much
> we do not. Together they are the scope statement — `NG` is not a footnote.

## Acceptance criteria — `AC` (draft)

Drafted per requirement so the reader can see what `R` means concretely. **Not** what HG1
approves — testability is judged mechanically at G1/G2, not by the human.

- **AC1** <observable pass/fail condition>   `covers: R1`   `in: COMP1`

## Dependencies & risks factored in

| Item | From | How it changed scope |
|------|------|----------------------|
| `D1` | spike | constrains `R1` — <how> |
| `RK1` | spike | justifies `NG1` — <how> |

## Assumptions — `ASM`

- **ASM1** <taken as true without evidence>   `affects: R1`   `state: open`

## Open questions — `OQ`

- **OQ1** <would change the work>   `affects: R1`   `state: open`

## Tags

`FEAT:` <FEAT#>   ·   `COMP:` <COMP#…>

## Scope approval (HG1)

Filled by `/ag-approve`. The human approves the **scope triple `P` + `R` + `NG`** — not this
document as a whole, and not the draft `AC`.

- **Approved by:** <name>   **at:** <UTC ISO8601>   → `DEC#`
- **`discovery_coverage` at approval:** <n>%   **open assumptions:** <n>
- **Assumptions accepted at the gate:** <ASM# … or "None.">

## Slices (filled at S4)

| Story | Requirements | Non-Goals |
|-------|--------------|-----------|
| `<N>.1` | R1 | NG1 |
