# Implementation Plan — <TASK_ID>

How agy should build it. Kept alive alongside the code through review. Names files,
approach, and sequencing — enough for agy to execute without re-deriving intent.

`FEAT:` <FEAT#>   ·   `COMP:` <COMP#…>

## Approach
<the intended shape of the solution in a few sentences — reuse existing utilities X, Y>

## Steps
- **IM1** <approach / files to touch>   `implements: AC1`   `in: COMP1`   `touches: <file#symbol>`
- **IM2** <...>   `implements: AC2, AC3`   `in: COMP1`

## Reuse (do NOT reinvent)
- <existing function/module agy should build on, with path>

## Constraints & guardrails
- Stay within `COMP#`; do not touch <areas>.
- Follow the commit convention: reference realized ids, e.g. `(AC2, IM1)`.

## Blockers / open questions
- <anything that must be resolved before or during implementation>
