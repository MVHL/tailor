# Brief for agy — <TASK_ID>

You are the implementer. Build exactly what makes the Test Plan pass, nothing more.
Work only inside this workspace. Do NOT merge, push, or delete branches.

## Ubiquitous language
<paste the relevant glossary terms + COMP definitions so agy uses the right words>

## Problem & requirements (context — do not re-scope)
- <P#: problem>
- <R#: requirement   solves: P#>
- Non-goals: <NG# — explicitly out of scope, do not build>

## Acceptance criteria (definition of done)
- <AC1: condition   covers: R#>
- <AC2: …>

## Test Plan — MAKE THESE PASS (TDD)
<paste TP.md tests + the run command. These already exist in the repo and currently FAIL.>

## Implementation Plan (how to build)
<paste IP.md steps, reuse notes, constraints>

## Rules
- Make the failing tests pass; do not weaken or delete tests to make them pass.
- Reuse existing utilities named above; match surrounding code style.
- Commit with the realized ids referenced, e.g. `feat: <desc> (AC2, IM1)`.
- When done, summarize what you changed and which ACs are now satisfied.
