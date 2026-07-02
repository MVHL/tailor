# Ticket Templates — Problem-Framed WoW

Copy-paste starting points for each artifact in the pipeline
(`jira-ticket-anatomy.html`). IDs and up-links follow the convention in
[`jira-trace-mechanic.md`](jira-trace-mechanic.md).

> **How to use:** copy the block, paste into the Jira description (or a
> Confluence page for the PRD), delete the `> guidance` lines, fill the rest.
> Keep the IDs — they are what makes the trace work.

---

## 1. PRP — Problem framing (Epic or pre-Epic)

> Lives in: the Epic (or a linked Confluence "PRP" page). Owner: BA/PM + Lead.
> Goal: capture the problem before any solution. One screen, no prose dumps.

```
## Problem Statement(s)
> Each: who is affected + what the impact is. Quantify if you can.
- P1: <who> <pain/opportunity> — <impact: %, tickets/week, $, time…>
- P2: <…>

## Success metric
> The number that tells us the problem is solved. Defines "done" at the outcome level.
- <metric, current value → target>

## Source
> Link, don't paste. Distilled decisions go above; raw discussion stays linked.
- <Slack thread / meeting notes / customer ticket links>
```

---

## 2. PRD — Sharpened & traceable (Epic)

> Lives in: the Epic description (canonical) or linked Confluence page.
> Owner: BA/PM. Produced after Three Amigos triage.

```
## Problem Statement(s)   (carried from PRP, sharpened)
- P1: <…>
- P2: <…>

## Requirements
> User-facing outcomes. Each MUST trace to ≥1 problem. One requirement may solve several.
- R1: <outcome>                          solves: P1
- R2: <outcome>                          solves: P1
- R3: <outcome>                          solves: P1, P2

## Non-Goals
> Acknowledged but excluded. Prevents scope creep. Deferred work links to a follow-up.
- NG1: <thing we are deliberately not doing>
- NG2: <deferred thing>                  deferred to: <KEY-123>
```

**Self-check before "Triage done":** every R has a `solves:`; every P has either
a matching R or appears in Non-Goals. (See DoR in `squad-playbook.html`.)

---

## 3. Story — Requirement slice + AC + plans (Story)

> Lives in: the Story. Owner: Dev (impl plan) + Tester (test plan), BA (AC).
> One story owns a slice of one or more requirements.

```
## Requirement slice
> Which requirement(s) from the PRD this story delivers. Link to the Epic/PRD.
- Delivers: R2 (from <EPIC-KEY>)

## Acceptance Criteria
> Observable, testable conditions. Each covers ≥1 requirement. Together: no gaps.
- AC1: <observable condition>            covers: R2
- AC2: <observable condition>            covers: R2

## Test Plan        (Tester/Dev — can start as soon as AC is final, no code needed)
> Happy / edge / error scenarios. Each maps to an AC.
- T1: [Happy] <scenario>                 covers: AC1
- T2: [Edge]  <scenario>                 covers: AC2
- T3: [Error] <scenario>                 covers: AC1

## Implementation Plan   (Dev — runs in parallel with the test plan)
> Enough to spot blockers early. Volatile detail stays in code/PR, not here.
- IM1: <approach / files to touch>       implements: AC1, AC2
- IM2: <…>                               implements: AC2
- Blockers / open questions: <…>
```

**Self-check before "Ready":** every AC has a `covers:`; every requirement slice
is covered by ≥1 AC; every AC has ≥1 test scenario.

---

## 4. Tech ticket — Enabler / non-user-facing

> Lives in: a Tech ticket linked to the Epic. Owner: Dev.
> Use when work has no direct user-facing AC (refactor, infra, migration).

```
## Why  (the enabler reason)
> What it unblocks. Link to the requirement/story that needs it if there is one.
- Enables: R3 / STORY-KEY   (or: tech-debt / infra — no parent requirement)

## Definition of Done
> Observable outcomes. Tech tickets still need testable completion criteria.
- DoD1: <observable / measurable result>
- DoD2: <…>

## Implementation Plan
- IM1: <approach / files>
- Blockers / open questions: <…>
```

---

## 5. Bug — lightweight path

> Most bugs do NOT need full P→R→AC framing. Use this trimmed form.
> Escalate to a Story only if the fix implies a new user-facing requirement.

```
## Problem
- What happens: <observed behavior>
- Expected: <correct behavior>
- Impact / scope: <who is hit, how often>
- Repro: <steps or link>

## Acceptance Criteria
- AC1: <observable fixed behavior>
- AC2: [Regression] <test that proves it stays fixed>
```

---

### ID quick reference

| Prefix | Artifact            | Up-link keyword |
|--------|---------------------|-----------------|
| `P#`   | Problem statement   | —               |
| `R#`   | Requirement         | `solves:`       |
| `NG#`  | Non-Goal            | `deferred to:`  |
| `AC#`  | Acceptance Criterion| `covers:` (R)   |
| `T#`   | Test scenario       | `covers:` (AC)  |
| `IM#`  | Impl plan step      | `implements:` (AC) |
