---
id:      C<N>
type:    charter
parent:  none
status:  draft              # draft → canonical (at HG0) → invalidated
blocked_reason: ""          # approval|decision|technical|budget|rejection-proposed
approved_by: ""             # set at HG0 — the human who made the bet
approved_at: ""             # UTC ISO8601
review_after: ""            # SL# or a slice count — MANDATORY re-bet trigger
appetite: ""                # e.g. "1 quarter" or "5 slices" — an INPUT, never an estimate
step:    S0
inputs:  []
score:   0                  # DERIVED by the board — never hand-set
jira:    ""
---

# CHARTER C<N> — <name of the bet>

A charter is a **bet, not a problem** (WORKFLOW R10). It holds a thesis, boundaries, an
appetite, ranked unknowns, and ordered slices. It **never** holds `P`/`R`/`NG`/`AC` — those
live in the child PRPs that its slices are minted into.

## Intake

- **SIG1:** "<verbatim evidence — the exact words of the ask, the quote, the link>"
- **ASK1:** <what was literally asked for>   `distilled from: SIG1`

> A charter's `ASK` does **not** license its children to skip evidence. Every child PRP
> gathers its own `SIG`.

## Thesis

<What becomes true if this succeeds. One paragraph. Not a problem statement — a claim about
the world that this bet asserts.>

## Outcome signals

How we would know the bet paid off. Leading indicators — **not** `AC`: outcome metrics, not
pass/fail checks.

- <signal — current value → what would count as the bet paying off>

## Boundaries — `BND`

What this charter explicitly is **not**. The charter-level analogue of `NG`; needs no up-link
because it bounds the charter itself. Slices cut for exceeding the appetite land here.

- **BND1** <excluded>   `reason: <why, or "beyond appetite">`

## Appetite

`<the declared bound>` — an **input**. When the slices exceed it, **cut slices** (they become
`BND`); do not extend the bound.

## Unknowns — `UNK` (ranked, most dangerous first)

The risky assumptions. This ranking is what makes "sequence by uncertainty" checkable.

- **UNK1** <the assumption this bet most depends on and least knows>
- **UNK2** <…>

## Slices — `SL` (ordered)

Each slice is a **thin end-to-end outcome someone can evaluate**. A slice that delivers only a
layer ("the data model", "the auth service") is not a slice — it fails the exit check.
`SL1` must reduce `UNK1`.

- **SL1** <title>
  - `hypothesis:` <the one-line problem this slice would solve>
  - `reduces: UNK1`
  - `needs:` — (none)
  - `state: hypothesis`   `minted: -`
- **SL2** <title>
  - `hypothesis:` <…>
  - `reduces: UNK2`
  - `needs: SL1`
  - `state: hypothesis`   `minted: -`

`state:` is one of `hypothesis` (not yet minted) · `in-flight` (minted, child in progress) ·
`done` · `cut`. `minted:` carries the child container id once `/ag-charter --mint` runs.

For a genuinely novel bet, the right `SL1` is often a **walking skeleton or a prototype**
rather than a feature — reducing the uncertainty beats decomposing the ask.

## Cross-cutting constraints

Inherited by **every** child. Each child's `IP.md` must cite these explicitly.

- <architecture / tech / compliance / data constraint that applies to all slices>

## Capability map (reference only — NOT the work breakdown)

Where code lives, i.e. the `COMP` set this charter touches. This answers *where*, while `SL`
answers *what next*. Conflating the two is how a charter silently becomes a horizontal plan.

- `COMP<n>` <name> — <dir/module>

## Bet log (append-only)

After each slice closes, `/ag-close` appends here. This is what a re-bet reads.

### <SL#> — <UTC ISO8601>
- **Outcome:** <what shipped>
- **Did the thesis hold?** <yes / partly / no — with the evidence>
- **Decision:** <continue / reorder / cut SL# / amend appetite / invalidate>   `→ DEC#`
