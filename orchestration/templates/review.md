---
id:      <N>.<M>            # or <N> for a G1 review at epic level
type:    review-framing     # review-framing (G1) | review-readiness (G2) | review-code (G3)
charter: none
status:  draft              # draft → canonical (when the verdict is final)
gate:    G1                 # G1 | G2 | G3
round:   1                  # loop round / agy iteration
verdict: fail               # pass | fail  — the gate's overall call
step:    G1
inputs:  []                 # the artifacts reviewed
score:   0                  # DERIVED — completeness of the grading, not of the work
---

# <G1 Framing | G2 Readiness | G3 Code> Review — <N>[.<M>] · round <n>

Produced by an **independent sub-agent** that has not seen the authoring rationale. This
independence is the point — a reviewer that saw the grill (G1) or the framing (G3) rationalizes
instead of assessing.

**Scope of this gate:** quality, never worth. A gate never rejects an item — that is a human
call at S2/S2b/HG1. If this review concludes "this shouldn't be built", raise it as an `OQ` and
route it to HG1 rather than failing the artifact.

## Verdict per input artifact

One verdict per artifact, never one verdict for the bundle — that is what lets a defect be
attributed to the step that produced it.

| Artifact | Verdict | Note |
|----------|---------|------|
| `prp-<N>.md` | pass / fail | <…> |
| `TP.md` | pass / fail | <…> |

## Findings — `F`

- **F1** <the defect, stated as one sentence>
  - `severity:` blocker | high | medium | low
  - `attributed-to:` S2   ← **the step that produced the defect**, not the step that found it
  - `resolution:` open | fixed | waived
  - `waiver:` `DEC#` — *(required when `resolution: waived`)*
  - `evidence:` <what in the artifact or diff shows this>

**Two ways to close a finding: fixed, or waived with a `DEC`.** Never "ignored".

**Waiver authority:** the Conductor may waive its own G1/G2 findings. It may **not** waive a G3
finding of `blocker`/`high` severity or any security finding — those require the human at HG2.

## Objective checks *(G3 only — run by the Conductor, mechanical)*

1. **TP tests run** — <command> → <green/red; note red→green>. Necessary, not sufficient.
2. **Diff read** — were tests edited, weakened, or deleted to pass? <yes → reject outright / no>
3. **Gamed-but-untouched tests** — for any test verifying a visual or content transformation,
   is the assertion satisfied by *real logic against the literal fixture data*, or merely by
   something of the right shape (a dummy marker, an element count)? <finding / clean>

Test-cheating is a **hard fail**: record it under *Discovered problems* and set
`metrics.quality.tests: 0`.

## AC grading *(G3 only)*

| `AC` | Grade | Evidence |
|------|-------|----------|
| AC1 | good / flagged / overdue | <passing test + clean impl / works but issues / not done> |

Prefer the sub-agent's grades over the Conductor's — that is what avoids self-scoring bias.

## Round log

| Round | Verdict | Findings raised | Fixed | Waived |
|-------|---------|-----------------|-------|--------|
| 1 | fail | 3 | 0 | 0 |

**Budgets:** G1 = 3 rounds · G2 = 2 rounds · G3 = 3 iterations. On exhaustion: stop, set the
artifact `status: blocked`, log a `DEC`, and escalate to the human with a crisp summary of what
remains.
