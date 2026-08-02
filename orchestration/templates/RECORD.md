---
task: <TASK_ID>
title: <one-line title>
status: in-review            # done | blocked | in-review | awaiting-decision
conductor: claude-opus-4-8   # who planned/reviewed
implementer: agy (<model>)   # who wrote the code
started: <UTC ISO8601>
closed: <UTC ISO8601 | ">
branch: <task-branch>
feat: <FEAT# | ">
comp: []                     # [COMP1, COMP2] touched
acs: []                      # [AC1, AC2] delivered
realizes: []                 # [AC1, IM2] this run realized
iterations: 0                # agy review-loop rounds
tests: <pass | fail | n/a>
mr: <link | ">
# metrics — see templates/scoring.md. 0–100 per step; raw analytics alongside.
metrics:
  frame:    { score: 0, grill_rounds: 0, decisions: 0, acs: 0, reframes: 0 }
  plan:     { score: 0, tests_planned: 0, red_captured: false }
  delegate: { score: 0, iterations: 0, agy_turns: 0, timeouts: 0, tokens: 0, seconds: 0 }
  review:   { score: 0, ac_good: 0, ac_flagged: 0, ac_overdue: 0, security_findings: 0 }
  overall_score: 0
---

# RECORD — <TASK_ID>: <title>

## What shipped
<1–3 sentences: what changed and where. Link the diff / MR.>

## Spec delivered
- Problem: <P# — one line>
- Requirements: <R# …>
- Acceptance criteria: <AC# — pass/fail each>
- Test Plan: [TP.md](./TP.md) · Impl Plan: [IP.md](./IP.md)
- Delegation transcript: [transcript.log](./transcript.log) · Decisions: [decisions.md](./decisions.md)

## Verification
- Tests: <command run> → <result; note red→green>
- Review: <standards + spec verdict; link review.md>

<!-- REQUIRED CLOSING SECTION — never omit, even if empty write "None." -->
## Assumptions
- <assumptions made while framing/planning/implementing>

## Discovered problems
- <problems found during the task that were outside the original scope>

## Possible bugs
- <suspected but unconfirmed defects; how to reproduce/confirm>

## Open issues
- <follow-ups, deferred items, tech debt, things to revisit — link Non-Goals if any>
