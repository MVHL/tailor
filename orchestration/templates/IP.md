---
id:      <N>.<M>
type:    ip
charter: none
status:  draft              # draft → canonical (at G2) → consumed (S7) → done (at S8)
blocked_reason: ""
step:    S6
inputs:  [<N>.<M>#AC1, <N>.<M>#T1]
score:   0                  # DERIVED
---

# Implementation Plan — <N>.<M>

How agy should build it. The Conductor does the *thinking*; agy does the *typing*. Concrete
enough that agy executes faithfully and a reviewer can check the result against it. Kept alive
through review — update it if the approach changes.

`FEAT:` <FEAT#>   ·   `COMP:` <COMP#…>

## Approach

<The intended shape of the solution in a few sentences. Name the seam it belongs in and what
must not cross it.>

## Steps — `IM`

- **IM1** <what to change and where>   `implements: AC1`   `in: COMP1`   `touches: <file#symbol>`
- **IM2** <…>   `implements: AC2, AC3`   `in: COMP1`

Sequence these so tests can go green incrementally. Every `AC` needs ≥1 `IM`; an `IM` with no
`implements:` is an orphan and fails G2. `touches:` is filled from the real diff at S8.

## Reuse (do NOT reinvent)

- `<path>` — <existing function/module agy must build on instead of writing its own>

An empty reuse list must be **explicitly justified** ("greenfield module, nothing to reuse") —
G2 treats a silently empty list as a finding, because it usually means nobody looked.

## Inherited charter constraints

*(Required when `charter:` is set — G2 checks that these are cited, not just inherited.)*

| From | Constraint | How this plan honors it |
|------|-----------|-------------------------|
| `C<n>` | <cross-cutting constraint> | <…> |

## Constraints & guardrails

- Stay within `COMP#`; do **not** touch <areas>.
- Do not weaken, skip, or delete tests to make them pass.
- Match surrounding code style; introduce no new framework or dependency.
- Commit convention: reference the realized ids, e.g. `feat: <desc> (AC2, IM1)`.
- Do not merge, push, or delete branches — the Conductor owns the merge.

## Open questions — `OQ`

- **OQ1** <must be resolved before or during implementation>   `affects: IM1`   `state: open`

> An `OQ` here that would change the *approach* should be answered before delegating. One that
> would only change a detail may be downgraded to an `ASM` and carried — say which.

## Assumptions — `ASM`

- **ASM1** <taken as true about the codebase or environment>   `affects: IM1`   `state: open`
