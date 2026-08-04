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
# metrics — see templates/scoring.md.
#   The board DERIVES both scores: the framing score from the P/R/AC/T/IM graph, and the
#   output score from the review counts + the closing sections below. Record the raw counts
#   honestly and the scores follow — do not hand-write an overall.
metrics:
  frame:    { grill_rounds: 0, decisions: 0, acs: 0, reframes: 0 }
  plan:     { tests_planned: 0, red_captured: false }
  delegate: { iterations: 0, agy_turns: 0, timeouts: 0, tokens: 0, seconds: 0 }
  review:   { ac_good: 0, ac_flagged: 0, ac_overdue: 0, security_findings: 0 }
  # optional — override a derived output dimension when judgement beats arithmetic.
  # Keys: acceptance | tests | defects | security | risk | followups
  # quality: { followups: 90 }
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
