---
name: ag-frame
description: Drive the framing phase (S1 Intake → S2 Discovery → S3 Specification → S4 Refinement) — verify signal→ask→problem, grill the human against a fixed coverage checklist, then produce canonical P/R/NG/AC. The front door of the orchestration loop; run before any planning or delegation. Use when starting a task, framing a problem, or when asked to "frame", "spec this", or hand work to agy.
---

# ag-frame — Phase A driver (S1 · S2 · S2b · S3 · S4)

You are **Role A (Author)**. You do **not** grade your own output: the assessor pass is a separate
gate (`ag-review-framing`, G1) run by an independent sub-agent that never sees this conversation.
Your job is to produce artifacts good enough to survive it.

This is `WORKFLOW.md` Phase A. Read §4 (step contracts, per-step notes, the Discovery coverage
checklist), §7 (sizing), and §12 (annotations) before starting.

**S2 is the highest-leverage step in the system.** Everything downstream is automatable exactly to
the extent that intent is recorded here. Spend the effort accordingly — and do not rush to
acceptance criteria.

## Inputs

A raw idea · a pasted/linked PRP · a bug report · a conversation · **or** a minted charter slice
(`slice: C<n>#SL<m>` — its hypothesis is your intake text). Plus `.orchestration/glossary.md` and
`graph.md`.

## Output artifacts

| Step | Writes |
|------|--------|
| S1, S2 | `epics/<n>/prp-<n>.md` — `SIG`, `ASK`, `P`, the coverage table, `ASM`, `OQ` |
| S3 | `epics/<n>/prd-<n>.md` — canonical `R`, `NG`, draft `AC` |
| S4 | `runs/<n>.<m>/story-<n>.<m>.md` (or `bug-` / `tech-`) — `R`/`NG` subset, canonical `AC` |
| any | `decisions.md` at the right level — one `DEC` per human exchange |

Collapsed form: S3 is skipped and everything lands in one `runs/<n>.1/<type>-<n>.1.md`.

---

## S1 — Intake

1. Allocate the container id (next from `epics/` + `runs/`); create the dir and `decisions.md`.
2. **`SIG`** — the *verbatim* evidence: the exact words, the error output, the quote, the link,
   with `source:` and `date:`. **Never paraphrase a signal.**
3. **`ASK`** — what the human literally asked *for*, `distilled from: SIG#`. This is a **solution
   hypothesis, not a requirement**. Never copy an `ASK` into an `R`.
4. Rule: *an ask with no signal is unfounded* — carry it as an `ASM` to test rather than silently
   accepting it.

**A bug starts at `SIG` like everything else** — its signal is the error output and repro steps.
That is machine-generated evidence, the strongest kind, and the only kind that later permits HG1
self-approval.

**From a charter slice:** the charter's `ASK` is inherited as *context*. You still gather at least
one local `SIG`. Otherwise one big ask launders into eleven invented problems.

## S2 — Discovery (the grill)

5. **`P`** — the underlying need behind the ask: `<who> <pain> — <impact with a metric>`,
   `evidence: SIG#/ASK#`. Separate *what they asked for* from *what they actually need*; these
   usually differ. A problem with no signal is an **invented need**.
6. **Work the coverage checklist** (`WORKFLOW` §4). Invoke `grill-with-docs` (or `grill-me`) and
   drive it against these eleven aspects, marking each `answered` · `assumed` · `n/a + reason`:

   | Group | Aspects |
   |-------|---------|
   | Problem depth | who is affected (+count) · frequency · impact with a metric · current workaround |
   | Scope split | which parts of `P` are solved (`R`) **and which are not** (`NG`) · deferral target per `NG` |
   | Reality | constraints · unspoken invariants · edge cases and failure modes · dependencies and risks |
   | Verification | how we will know it worked |

   A blank aspect is a G1 finding attributed to S2. Introduce new domain terms into `glossary.md`
   as they surface — pin down ambiguity while you have the human's attention.
7. **Log every question and answer as a `DEC`.** That is the auditable "why".
8. **Batch, don't stream.** If the human is unavailable, mark the aspect `assumed`, open an `ASM`,
   and **proceed** — they resolve the batch at HG1. But an `ASM` on a **scope** aspect (5 or 6)
   blocks HG1: you cannot approve scope that is itself assumed.
9. Compute `discovery_coverage` and record it beside the open-assumption count. **Coverage measures
   *considered*, not *known*** — 1.0 with six assumptions is well-surveyed, not well-understood.

### Two exits from S2 that are not S3

- **Reject** (`WORKFLOW` §5) if the problem dissolves — signal misread, already solved, impact
  negligible. You **propose**, the human confirms; `rejection_reason: dissolved`. Early rejection
  is a **success**, not a failure — never drag dead work into planning.
- **Escalate** to `ag-charter` if the §7 conditions hold: >1 unrelated `P` · no single `AC` set
  could demonstrate satisfaction · >2 `COMP` · sequencing decisions needed · `NG` acting as a
  roadmap. Also agent-proposed, human-confirmed.

### S2b — Spike (optional)

Run `ag-spike` only when the problem touches legacy or undocumented behavior, or when feasibility
is genuinely unknown. Most problems skip it. It emits `D`/`RK` and can also **reject**
(`infeasible`).

## HG1 — hand to the human; do not self-approve

Before HG1, run the **S3 exit check** (the mechanical `prd` ratios: no orphan `R`, every `R` has an
`AC`, every `NG` has `excludes: P#`, ≥1 `NG`). Then present via `/ag-approve`:

- the **scope triple `P` + `R` + `NG`** — that is what is approved
- the `discovery_coverage` report **and** the open-assumption list
- draft `AC` **shown** so `R` is concrete, but *not* what is being approved — testability is judged
  mechanically at G1/G2, not by the human

Self-approval is permitted only under the five conditions in `WORKFLOW` §5 (collapsed · coverage
1.0 with **zero** assumptions · no `D`/`RK` · **machine-generated `SIG`** · no new `COMP` or
glossary term) *and* only if this repo has an enabling `DEC`. Default is off. When in doubt, ask.

## S3 — Specification

10. **`R`** — outcomes that must be true: `solves: P#`, `part-of: FEAT#`. Feasibility confirmed;
    `D`/`RK` factored in.
11. **`NG`** — excluded scope, each with **`excludes: P#`** and a deferral target. `R` says how much
    of the problem we solve; `NG` says how much we don't. Together they *are* the scope statement —
    `NG` is not a footnote.
12. **`AC` (draft)** — one per requirement, so a reader sees what `R` means concretely.
13. Assign `FEAT` and `COMP`. Ids are append-only.

## S4 — Refinement

14. Slice the approved PRD into stories: each gets the `R`/`NG` **subset** it delivers, plus
    **canonical `AC`** (observable, testable, `covers: R#`).
15. **`P` is never re-authored.** Either reference the parent (`solves: 24#P2`) and embed a
    read-only **copy** of its text — the copy is a cache for agy's brief and the cold assessor, the
    pointer is truth — or own it locally when there is no parent.
16. Copy any inherited charter constraints into the story so `IP.md` can cite them.
17. One S4 session may emit **all** sibling stories (the R4 exception) — slicing needs to see the
    siblings to avoid overlap. Each emitted story still gets its own G1.

For a parentless item S4 is *authoring*, not slicing — same artifact, different input mode.

## Then stop

Report: the artifacts written, `discovery_coverage`, open `ASM`/`OQ` counts, and the next step
(`/ag-review-framing <id>` for G1). **Do not** run the assessor pass yourself, and do not proceed
into planning — G1 exists precisely because the author is the wrong judge of their own framing.
