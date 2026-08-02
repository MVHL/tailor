# Test Plan — <TASK_ID>

Authored BEFORE implementation (TDD). Every AC has ≥1 test; every test is pass/fail and
names how it is executed. agy's brief says "make these tests pass".

`FEAT:` <FEAT#>   ·   `COMP:` <COMP#…>

## Tests

- **T1** [Happy] <scenario — observable pass/fail condition>   `covers: AC1`
  - Executed by: `<test command / file path>`
- **T2** [Edge] <scenario>   `covers: AC1`
  - Executed by: `<...>`
- **T3** [Error] <scenario>   `covers: AC2`
  - Executed by: `<...>`
- **T4** [Regression] <only for bugs — the failing case that must stay fixed>   `covers: AC#`

## How to run
```bash
<the single command that runs all of the above>
```

## Red state (captured before delegation)
<paste the failing-test output here — proof the tests are meaningful>
