---
id:      <N>.<M>
type:    tp
charter: none
status:  draft              # draft → canonical (at G2) → consumed (at S7) → done (executed)
blocked_reason: ""
step:    S5
inputs:  [<N>.<M>#AC1, <N>.<M>#AC2]
score:   0                  # DERIVED
red_captured: false         # true once the failing output below is real
run_command: ""             # the ONE command that runs this plan
---

# Test Plan — <N>.<M>

Authored **before** implementation (TDD). Every `AC` has ≥1 test; every test is pass/fail and
names how it is executed. agy's brief says *"these exist and currently fail — make them pass"*.

`FEAT:` <FEAT#>   ·   `COMP:` <COMP#…>

## Tests

- **T1** `[Happy]` <scenario — the observable pass/fail condition>   `covers: AC1`
  - Executed by: `<test file path>`
- **T2** `[Edge]` <boundary input>   `covers: AC1`
  - Executed by: `<…>`
- **T3** `[Error]` <invalid input / failure handling>   `covers: AC2`
  - Executed by: `<…>`
- **T4** `[Regression]` <bugs only — the exact failing case that must stay fixed>   `covers: AC#`
  - Executed by: `<…>`

Every `AC` needs at least one test, and each should carry a happy, an edge, and an error case
unless one is genuinely inapplicable — say which and why.

## How to run

```bash
<the single command that runs all of the above>
```

## Red state (captured BEFORE delegation)

Paste the real failing output here. Red is what proves the tests measure something — a green
suite with no captured red state is scored as if the tests might be vacuous.

```
<paste the actual failing test output>
```

## Non-vacuity check

For each test, one line on **why it cannot pass without the feature**. A test that passes
against the unmodified codebase is worthless, and this is where that gets caught — not at G3.

| Test | Why it fails today |
|------|--------------------|
| T1 | <…> |

## Open questions — `OQ`

- **OQ1** <e.g. an untestable AC that needs rewording>   `affects: AC#`   `state: open`
