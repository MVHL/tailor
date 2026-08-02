---
name: ag-frame
description: Turn a raw idea, ask, or PRP into a canonical, gap-free spec (P/R/NG/AC) by verifying signal→ask→problem and grilling the human until the spec holds. The adversarial front door of the orchestration loop — run before any delegation. Use when starting a task, framing a problem, or when asked to "frame", "spec this", or hand work to agy.
---

# frame — grill until the spec is solid

You are **Role A (Author)** doing intake, and you switch to **Role B (Assessor)** to
break your own draft before it passes. A weak spec here poisons everything downstream,
so be adversarial, not agreeable. Do **not** rush to acceptance criteria.

## Inputs
A raw idea, a pasted/linked PRP, a bug report, or a conversation. Plus the current
`.orchestration/glossary.md`.

## Procedure

### 1. Intake — separate signal from ask (do not skip)
- **`SIG`** — capture the *verbatim* evidence: the exact words of the request, the error,
  the quote, the link. Never paraphrase a signal. `SIG1: "<verbatim>"`.
- **`ASK`** — what the human literally asked *for*. This is a **solution hypothesis, not
  a requirement**. `ASK1: <requested solution>   distilled from: SIG1`.
- Rule: *an ask with no signal is unfounded; carry it as an assumption to test.*

### 2. Distill the real problem
- **`P`** — the underlying need behind the ask. `P1: <who> <pain> — <impact>   evidence: SIG1/ASK1`.
- Rule: *a problem with no signal is an invented need* — challenge it or drop it.
- Separate "what they asked for" (ASK) from "what they actually need" (P). These often differ.

### 3. Grill the human (the core of this skill)
Invoke the `grill-with-docs` skill (or `grill-me`) and drive it against THIS spec.
Challenge relentlessly until answers stop changing the spec:
- Is the ASK actually the best solution, or just the first one imagined?
- Who is affected, how often, how badly? What is the cost of doing nothing?
- What are the edge cases, failure modes, and inputs at the boundaries?
- What is explicitly **out of scope** (→ Non-Goals)?
- What constraints exist (perf, compat, security, data, deadlines)?
- What must stay true that isn't being said (invariants)?
- Introduce new domain terms into `glossary.md` as they surface — pin down ambiguity.

**Log every question you ask the human and their answer as a `DEC` entry** in the run's
`decisions.md`. This is the auditable "why".

### 4. Decompose into the canonical spec
- **`R`** requirements — outcomes that must be true. `R1: <outcome>   solves: P1   part-of: FEAT1`.
- **`NG`** non-goals — deferred/excluded scope. `NG1: <excluded>   deferred to: <ref>`.
- **`AC`** acceptance criteria — observable pass/fail conditions. `AC1: <condition>   covers: R1   in: COMP1`.
- Assign `FEAT` (grouping) and `COMP` (bounded context) tags. IDs are append-only.

### 5. Assessor pass — try to break it (Role B)
Reuse the coverage checks from `jira-problem-framing`. Refuse to pass if any hold:
- **orphan requirement** — an `R` with no `solves:`.
- **bare requirement** — an `R` with no `AC` covering it.
- **uncovered AC** — none yet (tests come next) — but every AC must be coverable.
- **untestable AC** — not a clear pass/fail. Rewrite it.
- **problem with no R** — a `P` with neither a requirement nor a Non-Goal.
- **ask with no problem** — untriaged intake; resolve it.

## Output
Write `.orchestration/runs/<task-id>/spec.md` containing, in order: the `SIG`/`ASK`
trail, `P`, `R`, `NG`, `AC`, and the `FEAT`/`COMP` tags. Report the coverage-check
result.

## Stop conditions (ask the human, then continue)
Stop and ask when: the problem/scope is genuinely ambiguous, requirements conflict, or a
scope call is the human's to make. Otherwise proceed to `ag-plan`. Record the exchange
as a `DEC`.
