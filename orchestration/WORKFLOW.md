# WORKFLOW — the step contract

The authoritative definition of **what the steps are, what each one consumes, what it
emits, and when it passes**. Skills, commands, and the board all cite this document; where
any of them disagrees with it, this document wins and the other is to be corrected.

It supersedes the loose 5-activity loop described in `templates/CLAUDE.md` ("Frame → Plan →
Delegate → Review → Record") and §1 of `templates/scoring.md` (the task-level framing
score). Both are to be rewritten against this contract — see [Migration](#migration).

Aligned with the team's ways-of-working model: `wow/lifecycle-stages.html` (stage-primary)
and `wow/lifecycle-drivers.html` (artifact-primary). Same vocabulary, same status words,
same up-link direction.

---

## 1. Design rules

These are the reasons for the shape. A change that breaks one of them is a change to the
contract, not an implementation detail.

| # | Rule |
|---|------|
| **R1** | A step is a **pure function over artifacts**: declared IN set → declared OUT set. No step reads the conversation of a prior step. |
| **R2** | Every artifact is a **separately addressed file with frontmatter** (`id · type · status · score · inputs`). Status and score live on the artifact, not on the task. |
| **R3** | A step's OUT artifacts must be **self-contained enough for a cold evaluator**: an assessor given only the IN and OUT files, with no session history, must be able to grade it. This is what makes a step independently improvable. |
| **R4** | **One step per session.** `/ag <id>` advances exactly one step and stops. **One exception:** steps S1–S4 (the framing phase) may share a session, and a single S4 session may emit all sibling stories. Gates and build never share a session. |
| **R5** | Gates live on **edges**, not inside authoring steps. Entry gate = all IN artifacts at required status. Exit gate = checkable rules over OUT artifacts. |
| **R6** | Artifact status vocabulary is exactly the `wow` one: `draft → canonical → consumed → done`. The board then reads identically to `lifecycle-stages.html`. |
| **R7** | **The same actor never both authors and grades.** Every gate runs as an independent sub-agent that has not seen the authoring rationale. |
| **R8** | **Never vary the steps.** Vary how many documents the artifacts live in, and how deep the assessor reads. There is no "small task" flow — see [Sizing](#7-sizing--collapse-down-escalate-up). |
| **R9** | **The human decides scope and release; machines decide quality.** A human stop exists only where the choice is legitimately theirs — what to bet on (`HG0`), what to build (`HG1`), what to ship (`HG2`). Judging whether an artifact is *good* is a gate's job; a human doing that means a gate has failed. |
| **R10** | **A charter is a bet, not a problem.** The level above the PRP holds a thesis, boundaries, an appetite, and ranked unknowns — never `P`/`R`/`NG`/`AC`. Stretching the PRP chain to hold a platform-sized ask yields a `P` so abstract that every downstream check passes *vacuously*, which is worse than having no checks. |
| **R11** | **Slices are minted just-in-time.** A charter records slice *hypotheses*; a `SL` becomes a real PRP only when it is picked up. `SL1` is minted **alone** until the top-ranked `UNK` is reduced; after that, mint as many as the appetite and the review cadence allow. Pre-writing every child PRP up front is waterfall wearing this contract's vocabulary. |
| **R12** | **Rejection is a first-class outcome, and early rejection is a *success*.** Any item may be rejected at S2, S2b, or HG1 — with a recorded reason, never by deletion. Gates never reject: they judge quality, not worth (R9). The measure of health is the *stage* at which rejection happens, not its frequency. |

---

## 2. Levels, containers, and ids

Three levels, of which most work needs only the last two. The **charter** level owns the *bet*;
the **epic** level owns the *problem*; the **task** level owns the *deliverable*.

| Container | Holds | Exists when |
|-----------|-------|-------------|
| `charter-C<n>.md` | `SIG`, `ASK`, thesis, `UNK`, `SL`, `BND`, appetite | only when one ask exceeds a single epic — see §7 |
| `prp-<n>.md` | `SIG`, `ASK`, `P` | **always** — every entry point, chartered or not |
| `prd-<n>.md` | canonical `R`, `NG`, draft `AC` | only when the item is epic-backed (full form) |
| `story-<n>.<m>.md` · `bug-…` · `tech-…` | `R` subset, `NG` subset, canonical `AC` | always, one per task |
| `spike-<n>.md` | `D`, `RK` | only when a spike is run |

**Invariant: the PRP lives in the container that owns the `P`.** Epic-backed → the PRP sits
at the epic level and tasks reference its `P`. Standalone → the PRP is collapsed into the
task document, which owns its `P` locally.

**Invariant: a charter never holds a `P`** (R10). It holds slice *hypotheses* that become PRPs
when picked up. A charter with problem statements written into it has turned into a giant PRP
and has stopped doing its job.

**Invariant: a charter's `ASK` does not license its children to skip evidence.** Every child
PRP still needs its own `SIG`. Otherwise one big ask launders into eleven invented problems,
and the rule *"a problem with no signal is an invented need"* dies at exactly the scale where
it matters most.

### Id scheme

One monotonic counter for **containers** — epics and standalone items draw from the same
sequence (24 may be an epic, 25 a standalone bug). Children are dotted under their
container. **Task-level ids are always dotted, even when there is only one child**, so that
adding a sibling later never renumbers anything.

```
charters/C3/  charter-C3.md                        ← optional level above; its OWN namespace
epics/24/     prp-24.md  prd-24.md  spike-24.md    ← frontmatter: charter: C3, slice: C3#SL2
runs/24.1/    story-24.1.md   TP.md  IP.md  brief.md  review-*.md  RECORD.md
runs/24.2/    story-24.2.md   …
runs/25.1/    bug-25.1.md     …            ← collapsed form: SIG…AC in one file
```

Ids are **append-only**: never renumber, retire with a tombstone. No project-key prefix
locally — an external key goes in the `jira:` frontmatter field so our id and Jira's key are
never confused for one another.

**Charters get a separate namespace (`C3`), not a dotted prefix.** Container ids stay two-deep
(`24.1`, never `3.24.1`), and the charter→epic link lives in **frontmatter** (`charter: C3`),
not in the id. The reason is an asymmetry worth naming:

| Link | Where it lives | Why |
|------|----------------|-----|
| epic → task | **in the id** (`24.1`) | fixed at creation, effectively immutable |
| charter → epic | **in frontmatter** (`charter: C3`) | routinely decided *later*, and it changes — initiatives get re-cut and epics move between them |

Putting a mutable relationship into an append-only id is the renumbering trap this scheme
already avoided once. It also means a charter can be created **retroactively** over epics that
already exist — which is how a platform bet is usually recognized.

### Filenames vs. frontmatter

> **The filename is a label. The frontmatter is truth.**

Scanners glob `*-*.md` and read `type:` / `parent:`. A filename that goes stale (a bug
reclassified as a story) never breaks a tool — `git mv` is cosmetic cleanup, not a
correctness fix.

Which files carry an id in the name: the **spec-chain documents** (`prp`, `prd`, `story`,
`bug`, `tech`, `spike`), because they are referenced from other containers and pasted into
chats, so they must be self-identifying. Which do not: `TP.md`, `IP.md`, `brief.md`,
`review-*.md`, `RECORD.md` — never referenced from outside their own directory, and the
directory already carries the id.

### Item references

Item tags (`P1`, `R2`, `AC3`, `T1`, `IM2`, `DEC1`, `F1`, `ASM1`, `OQ1`, and the charter-level
`UNK1`, `SL2`, `BND1`) are numbered **per document**. `DEC` / `ASM` / `OQ` are *annotations* on
the chain rather than links in it — see §12.
Cross-document references must be qualified:

| Reference | Means |
|-----------|-------|
| `solves: P2` | `P2` **in this document** |
| `solves: 24#P2` | `P2` in container 24 |
| `covers: 24.1#AC3` | `AC3` in story 24.1 |

Unqualified = local; `<container>#<tag>` = foreign. An **unresolvable** up-link is an orphan
and fails G1. This is the one mechanism that lets a gate check traceability identically at
both levels.

### Frontmatter schema

Every artifact file opens with:

```yaml
---
id:      24.1              # container id this artifact belongs to
type:    story             # prp|prd|story|bug|tech|spike|tp|ip|review-framing|
                           #   review-readiness|review-code|record
parent:  24                # container id, or `none` for a root
charter: C3                # charter this belongs to, or `none` — MUTABLE, see §2
slice:   C3#SL2            # the charter slice this container was minted from, if any
form:    collapsed         # full | collapsed   (spec-chain documents only)
status:  canonical         # draft|canonical|consumed|done|blocked|stale
blocked_reason: ""         # approval|decision|technical|budget|rejection-proposed
                           #   — only when status: blocked
rejection_reason: ""       # dissolved|infeasible|not-now|duplicate|superseded (§5)
rejection_stage: ""        # S2|S2b|HG1 — the step it died at; late = expensive
approved_by: ""            # human who approved the scope triple (HG1) or the merge (HG2)
approved_at: ""            # UTC ISO8601
step:    S4                # the step that last wrote this artifact
inputs:  [24#P1, 24#R2]    # the artifacts/items consumed to produce it
score:   82                # last computed artifact score — DERIVED, never hand-set
jira:    ""                # optional external key
---
```

`score` is a cache of a computation the board can redo at any time (§8). Hand-editing it is
a defect.

### Status vocabulary (R6)

| Status | Meaning |
|--------|---------|
| `draft` | authored, not yet blessed by a gate |
| `canonical` | source of truth — downstream steps may consume it |
| `consumed` | sliced into, or superseded by, a downstream artifact; still readable, no longer edited |
| `done` | closed / shipped |
| `blocked` | cannot progress without a human decision; `blocked_reason` says which kind (`approval` · `decision` · `technical` · `budget`) so the board can separate "waiting on a person" from "waiting on a fix" |
| `stale` | an upstream artifact it depends on changed after it went canonical |
| `invalidated` | **charters only** — the bet was re-decided and abandoned at a re-bet review. Unminted `SL` are dropped; in-flight children stop or finish by explicit decision |
| `rejected` | terminal, human-confirmed: this will not be built. Carries `rejection_reason` and `rejection_stage`. The document stays — it is the answer when the same ask returns (§5) |

**Stale cascade:** editing a canonical `P` flips every child artifact that references it to
`stale`. Stale artifacts fail the entry gate of every downstream step until re-blessed.

---

## 3. The chain

```
Phase 0 — BETTING            (only for an ask bigger than one epic — §7 escalation)
  S0 Charter
        │
        ▓▓ HG0 — HUMAN approves the bet: thesis · appetite · slice sequence ▓▓
        │
        └─→ mint ONE slice (SL#) into a PRP, just-in-time (R11) ─┐
                                                                 │
            ◀── re-bet review after `review_after` ──────────────┘  (continue | amend | invalidate)

Phase A — FRAMING
  S1 Intake ─→ S2 Discovery ─(S2b Spike)─→ S3 Specification*
                                                 │
                          ▓▓ HG1 — HUMAN approves the scope triple  P + R + NG ▓▓
                                                 │
                                     S4 Refinement ─→ G1 Framing Review ⟲ (fix | waive+DEC)

Phase B — PLANNING
  S5 Test Plan ─→ S6 Impl Plan ─→ G2 Readiness Review ⟲

Phase C — BUILD
  S7 Implementation (agy) ─→ G3 Code Review ⟲ (budget 3)
                                                 │
                          ▓▓ HG2 — HUMAN approves the merge ▓▓
                                                 │
                                             S8 Close

  * S3 is skipped in the collapsed form; HG1 then sits between S2 and S4.

  Rejection exits — human-confirmed, on the record, never a deletion (§5):
    S2 ──rejected(dissolved)──┐
    S2b ─rejected(infeasible)─┼──→ status: rejected   ·   SIG returns to the unaddressed pool
    HG1 ─rejected(not-now)────┘                           `not-now` becomes an NG / BND
```

Backward edges exist **only** at the three gates. Everything else is forward-only.

`HG0` (once per charter, plus each re-bet), `HG1`, and `HG2` are the **only mandatory human
stops**. Everything between them loops until pass with no human involvement — see
[Human decision points](#human-decision-points).

Phase 0 is the only place with a loop above the item level: the charter is **re-decided**, not
just decomposed once.

---

## 4. Step contracts

| # | Step | Level | Actor | IN (required status) | OUT (emitted status) |
|---|------|-------|-------|----------------------|----------------------|
| **S0** | Charter *(oversized asks only)* | charter | Conductor (A) + human | an ask exceeding one epic (§7) | `charter-C<n>.md` *(draft)*: `SIG`, `ASK`, thesis, outcome signals, `BND`, appetite, ranked `UNK`, ordered `SL` |
| **HG0** | **Bet approval** | charter | **human** | `charter-C<n>.md` passing its exit check | charter *(canonical)*, `approved_by`/`approved_at`, `review_after` set, `DEC` logged |
| **S1** | Intake | epic\* | Conductor (A) + human | raw idea · PRP text · bug report · call note · **one minted `SL#`** | `SIG`, `ASK` *(canonical)*, `P` *(draft)* → `prp-<n>.md` |
| **S2** | Discovery | epic\* | Conductor (A) + human grill | `SIG`, `ASK` *(canonical)* | `P` *(canonical-candidate)*, `R`/`NG` *(draft)* → `prp-<n>.md` |
| **S2b** | Spike *(optional)* | epic\* | sub-agent | `P` *(canonical-candidate)* | `D`, `RK` *(canonical)* → `spike-<n>.md` |
| **S3** | Specification | epic | Conductor (A) | `prp-<n>.md`, `spike-<n>.md` if any | `R`, `NG` *(canonical)*, `AC` *(draft)* → `prd-<n>.md`; PRP → *consumed* |
| **HG1** | **Scope approval** | epic | **human** | `prd-<n>.md` passing its S3 exit check (or `prp-<n>.md` in collapsed form) + the **`discovery_coverage` report** + any open `assumption:` markers | `P`+`R`+`NG` *approved*: `approved_by`/`approved_at` stamped, assumptions resolved or waived, `DEC` logged |
| **S4** | Refinement | epic → task | Conductor (A) | `prd-<n>.md` *(canonical, approved)*, or `prp-<n>.md` in collapsed form | N × `story-<n>.<m>.md`: `R` slice, `NG` slice, `AC` *(canonical)*; PRD → *consumed* |
| **G1** | **Framing Review** | task | independent sub-agent (B) | the spec-chain documents **only** | `review-framing.md` *(canonical)* + artifact verdicts |
| **S5** | Test Plan | task | Conductor (A) | `AC` *(canonical)*, G1 pass | `TP.md` *(canonical)* + executable failing tests + captured red output |
| **S6** | Impl Plan | task | Conductor (A) + `Explore` | `AC` *(canonical)*, `TP.md` *(canonical)* | `IP.md` *(canonical)* |
| **G2** | **Readiness Review** (DoR) | task | independent sub-agent (B) | task doc, `TP.md`, `IP.md`, red output | `review-readiness.md` *(canonical)* + artifact verdicts |
| **S7** | Implementation | task | **agy** | `brief.md` (derived: task doc + TP + IP), G2 pass | code diff · commits · `transcript.log` · `result.iterN.json`; TP/IP → *consumed* |
| **G3** | **Code Review** | task | independent sub-agent (B) | diff, task doc, `TP.md` — **not** the framing rationale | `review-code.md` *(canonical)*: per-`AC` grade + findings |
| **HG2** | **Merge approval** | task | **human** | `review-code.md` verdict = pass, the diff, any waived findings | go / no-go on the merge; `DEC` logged. Delegable per repo — see §5 |
| **S8** | Close | task | Conductor | `review-code.md` verdict = pass, HG2 go | `RECORD.md` *(done)*, `graph.md` update, merge / MR; `Code` → *done* |

\* In the collapsed form, S1/S2/S2b write into the task document — the task owns its `P`.

`brief.md` is a **derived** artifact: mechanical assembly of the task doc + TP + IP, no
authoring judgment. It therefore carries no score of its own.

### Per-step notes

- **S0 — Charter.** For an ask too big for one epic ("build the platform"). Its content is a
  **bet**, not a problem (R10):
  - **Thesis** — what becomes true if this succeeds, in a paragraph.
  - **Outcome signals** — how we would know the bet paid off. Leading indicators, *not* `AC`:
    outcome metrics, not pass/fail checks.
  - **`BND`** — boundaries: what this charter explicitly is **not**. The charter-level analogue
    of `NG`, needing no up-link because it bounds the charter itself.
  - **Appetite** — the declared bound (a time box, or a slice count). An **input**, never an
    estimate that comes out. When the slices exceed it you **cut slices** — they become `BND` —
    rather than extending the bound.
  - **`UNK`** — the risky assumptions, **ranked**. This is what makes "sequence by uncertainty"
    checkable rather than aspirational.
  - **`SL`** — ordered vertical slices, each with a one-line problem hypothesis,
    `reduces: UNK#`, and an optional `needs: SL#` (acyclic) for genuine sequencing constraints.
    `SL1` must reduce the top-ranked `UNK` — not the easiest layer. Each slice is a thin
    end-to-end outcome someone can evaluate; a slice that delivers only a layer ("the data
    model", "the auth service") fails the exit check. `needs:` is recorded from day one even
    though v1 mints sequentially (§11), so parallel minting is later a scheduler change rather
    than a schema migration.
  - **Cross-cutting constraints** — architecture, tech, compliance, inherited by every child.
  - **Bet log** — append-only: after each slice, did the thesis hold? Continue / amend / cut.

  **The capability map is not the work breakdown.** A domain or capability map answers *where
  code lives* — that is `COMP` in `graph.md`, a reference artifact. `SL` answers *what we build
  next*. Conflating the two is how a charter silently becomes a horizontal plan.

  For a genuinely novel ask, the right `SL1` is often a **walking skeleton or a prototype**
  rather than a feature — reducing the uncertainty beats decomposing the ask. Route it through
  S2b Spike or the `prototype` skill.

- **HG0 — bet approval and re-bet.** The human funds the bet. `review_after` (a slice id or a
  count) sets a **mandatory** return: at that point the charter is re-approved, amended, or set
  `invalidated`. A charter with no scheduled re-bet is how zombie initiatives survive.

- **S1 — Intake.** `SIG` is captured **verbatim**, never paraphrased. `ASK` is labelled as a
  solution hypothesis, never copied into `R`. A bug's `SIG` is its error output and repro
  steps — machine-generated evidence, the strongest kind. A bug therefore starts at `SIG`
  like everything else; it is not a special entry point.
- **S2 — Discovery.** The human grill, and **the highest-leverage step in the system**: it is
  where the agent works alongside the human to establish *what problem we are solving* and
  *how much of it* (`R` vs `NG`). Everything downstream is automatable precisely to the extent
  that intent is recorded here. Every question asked and answered is logged as a `DEC`. `P`
  reaches *canonical-candidate*, not *canonical* — only G1 blesses it. Exit check: the
  coverage checklist below.
- **S3 — Specification.** Skipped entirely in the collapsed form.
- **S4 — Refinement.** For an epic-backed item this is **slicing**; for a standalone item it
  is **authoring**. Same OUT artifact, different input mode, so the board grid stays
  uniform. `P` is never re-authored here: a task either references a canonical `P` in its
  parent (`solves: 24#P2`) or owns it locally. When referencing, the task document embeds a
  **read-only copy** of the parent `P` text next to the pointer — the copy is a cache for
  agy's brief and for the cold assessor; the pointer is truth.
- **S5 — Test Plan.** Real executable tests land in the repo and the **red state is
  captured** into `TP.md`. Red is what proves the tests measure something.
- **S7 — Implementation.** Via `bin/agy-run.sh` only, in a worktree on `task/<id>`. agy never
  merges or pushes. Its self-report is never trusted; the diff and the test run are the
  source of truth.
- **S8 — Close.** If the task came from a slice (`slice:` is set), close **also appends to the
  charter's bet log**: did this slice's outcome support the thesis? That entry is what a re-bet
  reads. Without this hook the charter is a fan-out with no feedback.
  The Conductor owns the merge. `touches: <file#symbol>` anchors are filled
  into `IP.md` and `graph.md` from the diff. `RECORD.md` always closes with the four required
  sections (assumptions / discovered problems / possible bugs / open issues).

### How a charter leads the later steps

A charter is not a fan-out that then gets out of the way. It steers the chain below it in four
specific ways — and a `SL` item *is* the "smaller raw idea" that enters S1:

| Mechanism | Effect downstream |
|-----------|-------------------|
| **Order** | The `SL` sequence **is** the queue. Which PRP is minted next is a charter decision, not a task-level one. |
| **Inheritance** | The charter's cross-cutting constraints flow into **every child's `IP`**, which must cite them (§6). A child that ignores them can silently violate an architecture decision made at the bet level. `BND` likewise constrains what a child may pull into scope. |
| **Evidence pointer, not evidence** | `ASK` is inherited as context. Each child still gathers its **own `SIG`** — see the §2 invariant. |
| **Feedback** | Closing a slice (S8) appends to the charter's **bet log**, which may reorder, cut, or add `SL`. The charter is a control loop, not a one-time decomposition. |

**Minting.** `/ag-charter --mint <SL#>` creates the child container with `charter: C<n>`,
`slice: C<n>#SL<m>`, the slice's problem hypothesis as raw intake text, and the inherited
constraints. The child then runs the ordinary S1→S8 chain with no charter-specific variation —
per R8, nothing about the steps changes because a charter exists.

### Discovery coverage — the S2 exit check

Because S2 carries the most leverage, its coverage must be **countable like everything else**,
not left to the grill's thoroughness. Each aspect is marked `answered` · `assumed` ·
`n/a + reason`. An aspect left blank — neither answered nor explicitly assumed — is a G1
finding attributed to S2.

| | Aspect | Feeds |
|---|--------|-------|
| **Problem depth** | 1. Who is affected — role + rough count | `P` |
| | 2. Frequency — how often it bites | `P` |
| | 3. Impact — cost of doing nothing, with a metric | `P` |
| | 4. Current workaround — what they do today instead | `P`, `NG` |
| **Scope split** | 5. Which parts of `P` are solved (`R`) **and which are not** (`NG excludes: P#`) | `R`, `NG` |
| | 6. Deferral target for each `NG` | `NG` |
| **Reality** | 7. Constraints — perf, compat, security, data, deadline | `R`, `IP` |
| | 8. Invariants — what must stay true that nobody said out loud | `AC` |
| | 9. Edge cases and failure modes at the boundaries | `AC`, `TP` |
| | 10. Dependencies and risks — external actors, what could undermine this | `D`, `RK` |
| **Verification** | 11. How we will know it worked — the observable signal | `AC` |

`discovery_coverage` = `answered / (11 − n/a)`. It is reported to the human **at HG1**, so the
approval is made against known gaps rather than against prose alone — otherwise HG1 degrades
into a rubber stamp, which is the standard failure mode of an approval gate.

**Coverage measures *considered*, not *known*.** An aspect marked `assumed` counts toward
coverage — the checklist guarantees nothing was silently skipped, not that the answer is
right. `discovery_coverage: 1.0` with six assumptions is a well-*surveyed* problem, not a
well-*understood* one; the assumption count is the honest companion number and both are shown
at HG1.

*This list is v1 and domain-tunable — strike or add aspects to fit the kind of work this repo
actually receives. What is not negotiable is that the list is fixed, countable, and reported
at HG1.*

### Commands

| Step | Command | State |
|------|---------|-------|
| S0 | `/ag-charter` | **new** — authors the charter; `--mint <SL#>` seeds one PRP; `--review` runs the re-bet |
| HG0 | `/ag-charter` prompts for it | **new** — presents thesis · appetite · slice order · unknowns, records the bet |
| S1–S4 | `/ag-frame` (phase driver) | rewrite — loses its inline Assessor pass to G1 |
| S2b | `/ag-spike` | **new** |
| G1 | `/ag-review-framing` | **new** |
| S5 | `/ag-test-plan` | rewrite against ids |
| S6 | `/ag-impl-plan` | rewrite — loses its inline DoR gate to G2 |
| **HG1** | `/ag-approve <id>` | **new** — presents the scope triple + open assumptions, records the approval |
| G2 | `/ag-review-ready` | **new** |
| S7 | `/ag-delegate` | rewrite — review loop moves out to G3 |
| G3 | `/ag-review` | exists; becomes G3 explicitly |
| **HG2** | `/ag-close` prompts for it | rewrite — `/ag-close` asks for the merge go/no-go unless the repo has a recorded auto-merge `DEC` |
| S8 | `/ag-close` | rewrite against ids |
| — | `/ag-plan` | **retired** — S5 and S6 run separately |
| any | `/ag <id>` | advances exactly one step (R4) |

---

## 5. Gate contract

All three gates share one contract. They are steps in every respect — own session, own
artifact, own score. The only difference is a backward edge.

1. **Cold assessor (R7).** The gate runs as a fresh sub-agent given **only** its declared IN
   artifacts. G1's reviewer must not see the grill transcript; G3's must not see the framing
   rationale. Without this the gate rationalizes instead of assessing.
2. **Verdict per input artifact** — `pass` / `fail`, not one verdict for the bundle. This is
   what lets a defect be attributed to the step that produced it.
3. **Findings are itemized and attributed.** Each finding carries
   `F<n> · severity · attributed-to: S<step> · resolution: open|fixed|waived`.
4. **Two ways to close a finding: fixed, or waived with a `DEC`.** Never "ignored". Some
   findings are legitimately unfixable now ("we don't know the volume yet"); without a waiver
   path a strict gate deadlocks on unknowables. Waivers are counted and deduct from the
   artifact score, so the honesty property holds.
   **Waiver authority:** the Conductor may waive its own findings at G1 and G2, but **not** a
   G3 finding of high severity or any security finding — those require the human, at HG2.
   Otherwise G3 is toothless: the same actor would raise, waive, and ship the finding.
5. **Bounded loop, then escalate.** On exhaustion, stop, summarize precisely what remains,
   set the artifact `status: blocked`, log a `DEC`.

| Gate | Reviews | Loops with | Budget | Blocks |
|------|---------|-----------|--------|--------|
| **G1** Framing | `SIG ASK P R NG AC` | Conductor (A) | 3 rounds | Phase B |
| **G2** Readiness | `TP IP` vs. `AC` + spec consistency | Conductor (A) | 2 rounds | S7 |
| **G3** Code | diff vs. `AC`/`TP` | agy, same conversation | 3 iterations | S8 |

**Why framing needs two gates, not one.** A gate must sit adjacent to the step it evaluates,
or per-step scoring is meaningless. If one gate checked spec + TP + IP together, a broken
`AC` would surface only *after* someone wrote tests and an impl plan against it — wasted
work, and the finding could not be attributed to Discovery vs. Refinement vs. Planning.

No gate loops with the human. A finding that is genuinely a **scope call** is not resolved
inside the gate — it is routed to `HG1` (or `HG2` for a ship/no-ship call). Otherwise the
gate's `rounds` metric inflates with human latency and the step stops being independently
measurable.

**G3 never collapses and never softens.** It is the only thing standing between agy and
`main`. Its objective checks (run the tests, read the diff for weakened tests, check for
gamed-but-untouched tests) stay exactly as specified in the `ag-delegate` skill.

### Human decision points

Three kinds of human involvement exist and must not be confused (R9):

| Kind | Where | Automatable? |
|------|-------|--------------|
| **Information source** — only the human knows the answer | S1, S2 | **No.** The signal originates outside the system. |
| **Decision authority** — the choice is legitimately theirs | **HG0**, **HG1**, **HG2** | **No, and shouldn't be.** |
| **Quality assessor** — judging whether an artifact is good | G1, G2, G3 | **Yes** — that is what the gates are for. A human doing this means a gate has failed. |

**Human budget: ~3 touches per item** — one grill (S1/S2), one scope approval (HG1), one merge
approval (HG2). Per *item*, not per step. **Plus, per charter:** one bet approval and one re-bet
per `review_after` cycle. A charter therefore adds a *fixed* cost, not a per-slice one — which
is the point: the whole reason to hold the bet in one place is that the human decides it once
and then decides only whether to keep going.

**HG0 — bet approval.** The charter exit check verifies slice *shape* (vertical, uncertainty-
ordered, within appetite); the human makes the *bet*. Same division as everywhere else (R9):
machine judges quality, human decides direction.

**HG1 — scope approval.** After S3's exit check, **before S4**, so that no slicing, test
planning, or delegation is spent on unapproved scope. The human approves the **scope triple
`P` + `R` + `NG`** — *not* "the PRD" as a document: the PRD also carries draft `AC`, which is a
testability judgment G1/G2 make mechanically and which the human should not be adjudicating.
Draft `AC` is *shown* at HG1 because it makes `R` concrete, but it is not what is approved.
`P` is bundled rather than approved separately because approving `R` against a misunderstood
`P` is the expensive failure, and both come out of the same grill.

**HG2 — merge approval.** After G3, before S8. Merging to the default branch is irreversible
and outward-facing, and it is the one point where an automated decision reaches `main`.
Delegable per repo (e.g. *"auto-merge when G3 passes with no high-severity and no security
finding"*) — but the default is explicit, and the delegation is itself a `DEC`.

Both stops **emit a record**: `approved_by` / `approved_at` on the artifact plus a `DEC` in
`decisions.md`. An approval that leaves no record is not an approval — the board cannot show
"waiting on human" and no one can audit who said yes to the scope.

**Batch the human; do not stream them.** S2's grill is the real bottleneck, and a synchronous
grill puts the human in the *critical path* rather than in the loop. So S2 **may emit a `P`
carrying explicit `assumption:` markers and proceed** instead of blocking on an unavailable
human. Each assumption becomes a finding the human resolves at HG1 — one batched decision
instead of a stream of interruptions. An assumption still open at HG1 must be fixed or waived
with a `DEC`.

### Who may decide what

The autonomy dial, stated explicitly. It is narrow on purpose: everything an agent may decide is
a **quality or mechanics** call, and everything reserved for the human is a **direction or
irreversibility** call (R9).

| Tier | Decisions | Why |
|------|-----------|-----|
| **Human only — no confidence override** | **HG0** bet approval + every re-bet · **HG2** merge · rejection confirmation · appetite overrun · charter promotion · waiving a high-severity or security G3 finding | funding, direction, and irreversible acts. Confidence cannot substitute for a bet, because the uncertainty *is* the bet. HG2 is delegable only by an explicit standing per-repo `DEC` — never by per-item agent confidence |
| **Agent decides, human notified** | every gate verdict (G1, G2, G3) · all authoring steps S0–S6 · agy re-prompt iterations · minting the next eligible slice inside an already-approved charter · raising `blocked` | quality and mechanics — exactly what the cold assessors exist to judge |
| **Agent proposes, human confirms** | rejection at S2/S2b · escalation to a charter · splitting a collapsed item · any waiver in the first tier | the agent surfaces it early; the human owns the call |
| **Agent may self-approve HG1** | only under all five conditions below, always audited | the narrow band where no intent needs interpreting |

**When the Conductor may self-approve scope (HG1).** All five must hold:

1. the item is in **collapsed form** (below the §7 threshold);
2. `discovery_coverage` = 1.0 with **zero assumptions** — every aspect answered from evidence,
   none assumed;
3. no `D`, no `RK`, no rejection proposed;
4. the `SIG` is **machine-generated** — a stack trace, a failing test, a monitoring alert — **not
   a human ask**;
5. it introduces **no new `COMP`** and **no new glossary term**.

The common thread is condition 4: **no interpretation of intent is involved.** A human `ASK`
always requires interpreting what someone meant, and interpreting intent is the human's call.
What passes is essentially *unambiguous defect work* — the high-volume, low-judgment stream
worth automating, and nothing else.

Every self-approval is logged as a `DEC` marked `auto-approved` listing the conditions met, and
shown distinctly on the board. If an auto-approved item later fails G3 or produces a post-merge
defect, that counts against the policy: `auto_approval_failures` is the number that says whether
this dial is set too loose. Start with it **off** per repo and switch it on once there is evidence.

### Rejection — the cheap exit

An item that should not be built must be able to die **early and on the record**. Without this
path the only options are to drag dead work through planning or to delete it, and deletion loses
the answer for the next time the same ask arrives.

**Where rejection is allowed — and where it is not:**

| Point | Reject? | Why |
|-------|---------|-----|
| **S2 Discovery** | **yes** | the problem dissolves — `SIG` misread, already solved, impact negligible. The cheapest possible exit. |
| **S2b Spike** | **yes** | infeasible, incompatible with the existing system, or cost wildly past the appetite. This is what spikes are *for*. |
| **HG1** | **yes** | real, but not worth it now. A worth call, legitimately the human's. |
| **G1 · G2 · G3** | **no** | gates judge **quality, never worth** (R9). G1 says *"this spec is broken"*, never *"this shouldn't be built"*. |

**Who decides.** The Conductor may **propose** rejection at any step — `status: blocked`,
`blocked_reason: rejection-proposed`, with the evidence. Only a human **confirms** it, so R9
holds: the machine never decides worth, but it is free to surface dead work early rather than
dragging it through planning.

| `rejection_reason` | Consequence |
|--------------------|-------------|
| `dissolved` | the problem was not real. `SIG` retired with it. |
| `infeasible` | cannot be built as framed. `SIG` returns to the unaddressed pool — it may resurface with different `R`. |
| `not-now` | **must become an `NG`** on the parent PRD, or a `BND` on the charter, with a deferral target. Otherwise scope silently vanishes instead of being explicitly excluded. |
| `duplicate` | tombstone pointing at the container that absorbed it. |
| `superseded` | the charter was re-cut at a re-bet; unminted siblings usually go too. |

**Rejecting a `P` does not invalidate its `SIG`.** The signal does not stop being real because we
chose not to act on it. This is what keeps genuine evidence from being lost whenever something is
deprioritized — and it is why a rejected document is kept, not deleted.

**Early rejection is a success, not a failure** (R12). A rejected item must not count as a failed
task or drag any score down. What *is* measured is `rejection_stage`: killed at S2 is cheap and
healthy; killed at G3 means every upstream gate failed to notice. See §8.

**Interrupts — unplanned stops.** Beyond the two gates, the autonomy contract in
`templates/CLAUDE.md` still applies: stop and ask when scope is genuinely ambiguous,
requirements conflict, something is about to be built with no `AC`, an action is irreversible
or outward-facing, or agy exhausts its iteration budget. Set `status: blocked` with the
matching `blocked_reason` and log a `DEC`.

Interrupts are **defects with an owner**, not a normal mode. An interrupt firing repeatedly at
the same step means that step is under-specified — count them per step alongside gate findings.

---

## 6. Artifact registry — canonical when

The mechanical checks. Each is a **ratio** (share of items passing), never a boolean, so a
score degrades in proportion to how much is broken.

| Artifact | Items | By | Consumed by | Canonical when |
|----------|-------|----|-------------|----------------|
| `charter-C<n>.md` | `SIG` `ASK` `UNK` `SL` `BND` | S0, HG0 | S1 (one `SL` at a time) | appetite declared; ≥1 `BND`; every `SL` has a problem hypothesis **and** `reduces: UNK#`; every `SL` is vertical (an evaluable outcome, not a layer); `UNK` ranked and `SL1` reduces the top one; `needs:` graph acyclic; slices beyond the appetite explicitly cut to `BND`; `review_after` set; **bet approved at HG0** |
| `prp-<n>.md` | `SIG` `ASK` `P` | S1, S2 | S3 / S4 | every `SIG` has source + date and is verbatim; every `ASK` links ≥1 `SIG`; every `P` cites `evidence: SIG#/ASK#`; every `P` has ≥1 `R` or `NG`; **`discovery_coverage` = 1.0** (every aspect answered, assumed, or `n/a` with a reason) |
| `spike-<n>.md` | `D` `RK` | S2b | S3 | every `D`/`RK` links the `P#` it came from; `D` names an external owner; `RK` states likelihood + impact |
| `prd-<n>.md` | `R` `NG` `AC`(draft) | S3, HG1 | S4 | no orphan `R` (all have resolvable `solves:`); every `R` has ≥1 `AC`; ≥1 `NG` recorded; `D`/`RK` visibly factored into `R`/`NG`; **every `NG` links `excludes: P#`** — the unsolved share of each `P` is explicit, not implied; **scope triple approved at HG1** (`approved_by` set, no open `assumption:`) |
| `story-<n>.<m>.md` | `R` slice · `NG` slice · `AC` | S4 | S5, S6, S7, G3 | every `AC` has `covers: R#` and is observable pass/fail; every `R` slice resolves upward; `P` either owned locally with evidence, or referenced + cached |
| `TP.md` | `T` | S5 | S7, G3 | every `AC` has ≥1 `T`; `[Happy]`/`[Edge]`/`[Error]` present per `AC` (`[Regression]` for bugs); one run command; **red output captured**; no vacuous test |
| `IP.md` | `IM` | S6 | S7 | every `AC` has ≥1 `IM`; no orphan `IM`; reuse list non-empty or explicitly justified; constraints + guardrails stated; **any inherited charter constraints cited explicitly** (§4) |
| diff / `Code` | commits | S7 | G3, S8 | commits reference the ids they realize; no test weakened or deleted |
| `review-*.md` | `F` | G1/G2/G3 | next step, S8 | every input artifact has a verdict; every finding attributed to a step; every finding `fixed` or `waived` with a `DEC` |
| `RECORD.md` | metrics | S8 | board | four closing sections present; `touches:` anchors filled from the diff; `metrics` counts recorded honestly |

---

## 7. Sizing — collapse down, escalate up

Per **R8**: the steps never vary. What varies is the number of documents and the assessor's
depth. There is no separate flow for small work, because the steps are what make scores
comparable — a short path that skips G1 would destroy per-step attribution for exactly the
class of work that is most numerous.

| | Full form | Collapsed form |
|---|---|---|
| Documents | `prp-24` → `prd-24` → `story-24.1…n` | one `story-24.1.md` / `bug-24.1.md` holding `SIG · ASK · P · R · NG · AC` |
| S1–S4 | 4 sessions | **1 session, still 4 scored steps** |
| G1 + G2 | 2 gate sessions | **1 session, still 2 verdict blocks** |
| S3 | runs | skipped |
| **HG1** | between S3 and S4 | **between S2 and S4 — still mandatory** |
| **HG2** | before S8 | **before S8 — still mandatory** |
| S5, S6 | separate sessions | separate sessions (unchanged) |
| S7 + G3 + S8 | unchanged | **unchanged** |
| Sessions | ~10 | ~4 |

Identical metrics from both forms: same items, same tags, same gate checks — only
co-located.

### Escalation — when an ask needs a charter

The mirror of the collapse threshold, and judged the same way: **by the outcome of Discovery**,
never by how the ask was phrased. Escalate to a charter when, after S2, *any* hold:

- the ask yields **>1 `P`** that do not share a single measurable impact
- **no single `AC` set** could demonstrate the ask is satisfied
- it spans **>2 `COMP`** (bounded contexts)
- it needs **sequencing decisions** — some parts only make sense after others land
- its `NG` set is doing the work of a roadmap rather than bounding one problem

One escalated ask becomes `charter-C<n>` + ordered `SL`; each `SL` is minted into its own PRP
just-in-time (R11). **A charter is never collapsed** — collapse is a form for items *below* the
threshold, and a charter exists precisely because the ask is above it.

Escalation may also happen **retroactively**: three epics turn out to be one platform bet, so a
charter is written over them and their frontmatter gains `charter: C<n>`. No renumbering — that
is what the frontmatter link in §2 buys.

### Threshold (mechanical, not a judgment call)

Determined **by the outcome of Discovery**, never declared upfront. Stay collapsed while
*all* hold:

- exactly **1** `P`
- **≤3** `R`
- **≤5** `AC`
- **no** `D` and **no** `RK`
- **one** `COMP`

Break any one → split into full form, keeping the container id. The collapse choice is
logged as a `DEC` **and re-checked by G1**, so an item that under-declared itself is caught
by the cold assessor rather than by nobody.

### Growth path

`bug-24.1.md` outgrows the threshold → promote to `prp-24.md` + `prd-24.md`, tombstone the
collapsed document, and `story-24.1` keeps its id and its item tags. Nothing renumbers —
which is the reason task-level ids are always dotted (§2).

**Not yet designed:** a `D` or `RK` surfacing *after* collapse forces a mid-flight split. The
transition is unspecified; treat it as a human decision and log a `DEC`.

---

## 8. Scoring

Three levels, each derived from the one below. Nothing is asserted by whoever closed the
task; the board can recompute all of it from the files.

**1. Artifact score** — the atom.

```
artifact_score = (weighted mean of its §6 ratios × 100) − 10 × (findings attributed to it
                  that are open or waived)          … clamped to 0–100
```

Checks whose artifact does not exist yet are **skipped, not failed** — an item mid-planning
is not punished for work it has not reached.

**2. Step score** = mean of that step's OUT artifact scores. *This* is the number that makes
a step independently improvable: "Discovery averages 62 across 9 epics" is actionable in a
way "task scored 78" never was.

**3. Phase roll-ups.**

| Roll-up | From |
|---------|------|
| **Framing score** | Phase A + Phase B step scores (S1–S6, G1, G2) |
| **Output score** | `templates/scoring.md` §2 dimensions, driven by G3 + S8 |
| **Charter health** | its own §6 ratios, plus `appetite_burn` (slices minted ÷ appetite) and `thesis_held` from the bet log |

**Charter health is deliberately *not* a roll-up of its children's scores.** A charter can be
full of well-framed, cleanly-shipped slices and still be a losing bet — that is what the bet log
and `thesis_held` record. Averaging the children would hide exactly the failure the re-bet exists
to catch.

The two headline numbers survive unchanged in meaning — they are now decomposable into the
steps that caused them.

**The intake hypothesis — the one this design is betting on.** *"Once intent is clearly
recorded, the rest automates."* This model makes that testable rather than aspirational:
`discovery_coverage` (§4) should predict `interrupts` at S5–S7, G1 findings attributed to S2,
and G3 iteration count. If thin intake does **not** show up downstream, the coverage checklist
is measuring the wrong aspects and should be retuned. That correlation is the single most
valuable analytic the board can produce.

**Rejection metrics.** A `rejected` item is **excluded from framing and output score
distributions** — scoring it would punish the workflow for working (R12). What is tracked instead:
`rejection_stage` and `rejection_reason`, and per charter, the share of slices rejected. Read them
this way:

| Pattern | Reading |
|---------|---------|
| rejections concentrated at **S2 / S2b** | healthy — the cheap gates are doing their job |
| rejections at **HG1** | scope discipline working, but Discovery is surfacing worth-questions late |
| rejections at **G2 / G3** | a defect: every upstream step missed it. Investigate the step, not the item |
| a charter with **most slices rejected at S2b** | the *thesis* is wrong, not the slices. Trigger a re-bet |

**Autonomy metrics.** `auto_approved` (count of self-approved HG1s) and
`auto_approval_failures` (those that later failed G3 or produced a post-merge defect). The ratio
is the only evidence that the §5 self-approval conditions are set correctly — a non-zero failure
rate means tighten them, not explain them away.

**Human-cost metrics** (per item, into `RECORD.md`): `human_touches` (target 3),
`hg1_latency` / `hg2_latency` (approval wall-clock), `interrupts` with the step each fired at,
and `assumptions_waived` at HG1. These measure whether the automation claim actually holds —
a rising `interrupts` count at one step is that step asking to be re-specified.

**Gate metrics** (per gate, into `RECORD.md`): `rounds`, `findings_raised`,
`findings_waived`, and each finding's `attributed-to` step. That last field is the payoff:
*"G1 raised 14 findings across 6 epics, 11 of them against Discovery"* is how a step gets
improved in isolation. It also honestly replaces `metrics.frame.grill_rounds`.

**Caps** carry over from `scoring.md`: `status: blocked` or `tests: fail` caps the overall at
**40**. The guiding property is unchanged — **a low score must mean more real problems**,
every deduction tied to a countable item.

---

## 9. File layout

```
.orchestration/
  glossary.md                  # ubiquitous language (DDD)
  graph.md                     # FEAT/COMP + spec↔code↔run links + parent/child links
  current-task                 # dotted id of the active task (sub-agent hook nesting)
  charters/
    C3/
      charter-C3.md            # SIG · ASK · thesis · BND · appetite · UNK · SL · bet log
      decisions.md             # DEC — charter-level (bets, re-bets, cuts)
  epics/
    24/
      prp-24.md                # SIG · ASK · P
      prd-24.md                # R · NG · AC(draft)
      spike-24.md              # D · RK          (optional)
      decisions.md             # DEC — epic-level (scope approvals, interpretation, waivers)
                               #   ASM / OQ live INLINE in the documents above, not here (§12)
  runs/
    24.1/
      story-24.1.md            # R slice · NG slice · AC
      TP.md  IP.md  brief.md
      review-framing.md  review-readiness.md  review-code.md
      transcript.log  result.iterN.json
      running.json             # transient: present only while agy is delegating NOW
      decisions.md  RECORD.md
    25.1/
      bug-25.1.md              # collapsed: SIG · ASK · P · R · NG · AC
      …
    index.md                   # running log across all tasks
  agents/                      # Claude sub-agent breadcrumbs (one JSON per spawn)
  worktrees/<id>/              # throwaway worktree per task branch
```

---

## 10. What the board renders

A **task × step grid**: one row per task, one cell per step (S1…S8 + G1/G2/G3), each cell a
status dot plus a score. Clicking a cell shows exactly its declared **IN chips** and **OUT
chips** — a handful each, per R1.

Alongside it, an **open threads** panel: every `ASM` and `OQ` still `open` across the repo,
grouped by container, with age. This is the *centralized view* over decentralized records (§12) —
derived, never authored. "What unknowns are we carrying?" must be answerable without opening
forty files.

Above it, a **charter view** for each `charter-C<n>`: the thesis, the appetite burn, and the
ordered `SL` list with each slice's state — `hypothesis` (not yet minted) · `in-flight` (minted,
epic in progress) · `done` · `cut`. Plus the bet log and the next `review_after`. This is the
level at which "what is the state of the platform bet?" is answerable at a glance, without
reading any child document. Charter-level rows are the entry point; the task grid is the drill-in.

Because statuses are the `wow` vocabulary (R6), the grid reads identically to
`lifecycle-stages.html` with a score added per cell. The two views stay consistent by
construction rather than by discipline.

---

## 11. Dispatch — the one command

`/ag` is the only entry point a human needs. It never asks which step you are on — it derives
that from the files.

| Input | Behaviour |
|-------|-----------|
| `/ag` | Status: the charter view, the task grid, and the single next action per live item. Then stop. |
| `/ag <container-id>` | Resume: detect the current step from the files, advance **exactly one** (R4), stop. |
| `/ag "<new ask>"` | Intake a new ask — sized per the rule below, not by its wording. |
| `/ag <charter-id> --mint` | Mint the next eligible `SL` into a PRP and start its framing session. |
| `/ag <id> --to <step>` | Explicit chaining — the only way to advance more than one step, and it **still halts** at HG0 / HG1 / HG2. |

### Sizing is decided by evidence, not by phrasing

`/ag "<new ask>"` does **not** branch on how the ask was worded. *"Just add SSO"* can be a quarter
of work; *"rebuild the reporting platform"* can be one config change. So it always runs
**S1 → S2**, then applies the §7 escalation test to what Discovery actually produced:

- **escalates** → the in-progress PRP is **promoted** to a charter: `SIG`/`ASK` carry over, the
  draft `P`s become `UNK`/`SL` hypotheses, the container id is preserved (§7 retroactive
  chartering, no renumbering). Promotion is *agent-proposed, human-confirmed*.
- **does not escalate** → continue into S3/S4, or stay collapsed.

A cheap **pre-screen** may *propose* the charter route before the grill starts, so an obviously
platform-sized ask is not grilled as though it were one problem. The pre-screen is **advisory
only** — S2's evidence confirms or overturns it, and the proposal is recorded either way.

### `ag-close` is the scheduler

S8 decides what happens next, so no human has to remember. After the record is written and the
merge is done:

1. if `slice:` is set → append the **bet-log** entry (did this outcome support the thesis?);
2. if `review_after` has been reached → **halt and request the re-bet** (HG0). Do not mint;
3. else → compute the **mintable set** and mint the next work, or report the charter complete;
4. if the item was standalone → report done, no further action.

**Mintable set.** A `SL` is mintable when every `needs: SL#` is closed — and, until the
top-ranked `UNK` is reduced, **only `SL1` is mintable at all** (R11).

| Phase | Behaviour |
|-------|-----------|
| **v1 — build this first** | Mint **one at a time**, sequentially, until the list is done. Simpler, and it keeps the bet log meaningful: each slice's outcome is read before the next starts. |
| **v2** | Mint the whole mintable set in parallel. `needs:` already exists in the schema, so this is a scheduler change only. |

Dispatch never crosses a human gate. When the next step is HG0, HG1, or HG2, `/ag` stops and says
exactly what it needs — even under `--to`.

## 12. Decisions, assumptions, and open questions

**They are items, not artifacts.** An artifact is a step's output with a status and a score;
these are **annotations on the chain**, emitted as a side effect of many steps. Giving each one a
file would explode the file count and destroy the handful-of-chips property §10 depends on.

The forward chain (`P → R → AC → T/IM → code`) is scored for **coverage**. Annotations are scored
for **resolution**. Two different questions, deliberately separate.

### The three types

| Tag | What it is | Lives | Resolves when |
|-----|-----------|-------|---------------|
| `DEC` | a decision that was made, and why | `decisions.md` at the level whose **scope it binds** | never — append-only and immutable |
| `ASM` | something taken as true **without evidence** | **inline** in the artifact it annotates, next to the item it affects | evidence arrives (confirmed / refuted), or it is explicitly accepted at a human gate |
| `OQ` | a question whose answer **would change the work** | **inline** in the artifact it annotates | answered (→ becomes a `DEC`), or downgraded to an `ASM` to unblock |

`ASM` and `OQ` are inline rather than in a sibling file so that a cold assessor grading that
artifact sees them without traversing (R3). They carry an inline state:
`ASM2: <text>   affects: P1   state: open`.

### They convert into each other — that is the mechanism

```
  OQ ──answered──────────→ DEC              (the question is settled; record why)
  OQ ──cannot answer now─→ ASM              (proceed explicitly rather than silently)
  ASM ──tested, holds────→ DEC              (promote to a decision)
  ASM ──tested, fails────→ RK  or  F        (a risk, or a gate finding)
  F  ──needs a call──────→ OQ               (a gate finding that is really an open question)
```

This is what makes the automation claim honest: the Conductor can **proceed on an `ASM` instead
of blocking**, which is exactly the batching rule in §5. `ASM` was already load-bearing in this
design — it just had no name.

**A `DEC` is never edited.** A reversed decision is a *new* `DEC` carrying
`supersedes: DEC3`. Same append-only rule as ids.

### Which level owns a `DEC`

> **A `DEC` lives at the level whose scope it binds** — not the level where it happened to surface.

| Level | Typical `DEC`s |
|-------|----------------|
| `charters/C<n>/decisions.md` | bets, re-bets, slice cuts, appetite calls, cross-cutting architecture constraints |
| `epics/<n>/decisions.md` | HG1 scope approvals, problem interpretation, `not-now` rejections, G1 waivers |
| `runs/<n>.<m>/decisions.md` | planning calls, agy iteration decisions, Conductor direct edits, HG2 merge approval |

A decision that constrains every slice belongs to the **charter**, even if it was discovered
while building slice 3. Otherwise charter-level constraints get buried in a task directory where
no sibling will ever read them.

### One guard, and it is not arbitrary

An `ASM` is permitted almost anywhere — but **an `ASM` on a scope aspect blocks HG1**
(Discovery-coverage aspects 5 and 6: which parts of `P` are solved, and each `NG`'s deferral
target). You cannot approve scope that is itself assumed. Assumptions about constraints, volumes,
or edge cases are fine to carry through the gate; assumptions about *what we are building* are
not.

Without this, `ASM` becomes the way to skip the grill entirely — every hard question converted to
an assumption and waved through.

### At close

`RECORD.md`'s closing sections become **roll-ups, not freshly authored prose**:

| Section | Source |
|---------|--------|
| Assumptions | `ASM` still `open` at S8 |
| Open issues | `OQ` still `open` at S8 — these feed `scoring.md`'s *followups* dimension |
| Discovered problems | unchanged — and each one is **mintable as a new `SIG`**, closing the loop back into intake |
| Possible bugs | unchanged |

*Discovered problems* and *possible bugs* stay as they are: they are findings about reality, not
unknowns about intent, and they are the seed material for the next item rather than debt on this
one.

## Migration

Consequences of adopting this contract, in dependency order:

1. `templates/` gains `charter.md`, `prp.md`, `prd.md`, `story.md` skeletons; `TP.md`, `IP.md`,
   `RECORD.md` gain the §2 frontmatter.
2. `templates/CLAUDE.md` — replace the 5-activity loop with this chain; add the id scheme and
   the item-reference syntax to the traceability table.
3. `templates/scoring.md` — §1 (framing score) is superseded by §8 here; §2 (output
   dimensions) survives and is cited by it.
3b. `templates/IP.md` — "Blockers / open questions" becomes `OQ` items (§12).
    `templates/RECORD.md` — "## Assumptions" and "## Open issues" become **roll-ups** of open
    `ASM`/`OQ` rather than hand-written prose, removing today's three overlapping vocabularies for
    the same concepts. `templates/decisions.md` gains `supersedes:` and the level-ownership rule.
4. `skills/ag-frame` — becomes the Phase A driver, and its grill section is restructured around
   the **Discovery coverage checklist** (§4) so intake produces a countable coverage report
   instead of an unstructured conversation. Its inline Assessor pass **moves out** to
   G1. `skills/ag-impl-plan` — its inline Definition-of-Ready gate **moves out** to G2. In
   both cases the author currently blesses their own work, which R7 forbids.
5. New skills: `ag-review-framing` (G1), `ag-review-ready` (G2), `ag-spike` (S2b).
6. `skills/ag-delegate` — the bounded review loop moves out to G3; the skill keeps worktree
   setup, brief assembly, and adapter invocation.
7. `commands/ag.md` — rewritten to §11: one entry point, evidence-based sizing (not
   phrase-based), advance exactly one step (R4), `--to` for explicit chaining, and **halt at
   HG0/HG1/HG2** rather than advancing through them. Its current §4 ("run the full loop") is the
   behaviour this contract exists to remove. `/ag-close` becomes the scheduler (§11).
8. New `/ag-approve` command (HG1) and a merge prompt in `/ag-close` (HG2); `templates/CLAUDE.md`'s
   autonomy contract is rewritten as *two mandatory stops + named interrupts* rather than a
   list of conditions to notice.
9. New `/ag-charter` command + `skills/ag-charter` (S0/HG0, minting, re-bet); `commands/ag.md`
   dispatch learns the charter level and the §7 escalation check after S2.
10. `bin/ag-dashboard.py` — scanner rewrite: parse N artifact frontmatters per task instead of
   one `RECORD.md`; render the grid of §10, and surface `blocked_reason: approval` distinctly
   so an approval backlog never reads as an engineering backlog.

## Known limitations

- **Id allocation races.** Two concurrent branches both pick 26. Neither a counter file nor
  max-of-existing survives that. Mitigation: allocate the id at intake, on the default
  branch, before branching. The residual risk is accepted rather than solved with a registry.
- **Re-parenting costs a tombstone.** Putting the parent in the child's id means moving
  `24.2` under epic 27 requires reissue. Accepted for the readability on every read;
  `parent:` in frontmatter stays authoritative if an id ever reads stale.
- **Post-collapse `D`/`RK`** forces a mid-flight split with no designed transition (§7).
- **Stale cascade needs a graph change.** `graph.md` currently records only `AC`/`IM` → run →
  `touches:`; parent/child container links are an addition to its schema, not a rename.
- **Three gates roughly triple the sub-agent sessions per task.** They buy per-step
  attribution and real A/B separation. The ~4-vs-~10 figures in §7 are **session counts, not
  measured tokens** — no cost baseline exists for the current system, so the true delta is
  unquantified.
- **No counterpart for `wow`'s sprint Planning, QA, or Deployment stages.** There is no
  sprint or release object in this system. G3 covers the review portion of QA only;
  deployment is out of scope.
- **S2's grill remains the throughput ceiling.** The assumption-marker escape hatch (§5) keeps
  the loop moving when the human is away, but an item whose `P` is genuinely unknown without
  them cannot be framed by machine. Automation here is bounded by information, not by design.
- **HG1 latency is unmodelled.** Two mandatory approvals mean an item can sit idle for days
  with every machine step already passing. The board must show `blocked_reason: approval`
  distinctly or the queue will look like an engineering backlog when it is an approval backlog.
- **Delegated HG2 is a real risk surface.** A repo that switches on auto-merge has removed the
  only human check between agy and `main`, leaving G3 as the sole guard. Recommended only where
  the test suite genuinely gates correctness.
- **`ASM` is the pressure-relief valve, which makes it the abuse vector.** The scope-aspect guard
  (§12) stops the worst case, but nothing prevents a Conductor from converting every awkward
  question into an assumption and proceeding. The visible controls are the assumption count shown
  at HG1 and the score deduction per open annotation — both rely on the count being reported
  honestly. Watch `ASM` created per item over time; a rising trend means the grill is being
  skipped.
- **HG1 self-approval is the riskiest thing in this contract.** Its five conditions are reasoned,
  not measured, and condition 4 (machine-generated `SIG`) is the only one that is objectively
  checkable — the others depend on the Conductor's own honest reporting of its own coverage.
  Default it **off** per repo; turn it on only with `auto_approval_failures` evidence.
- **The pre-screen can bias Discovery.** A pre-screen that proposes "this is charter-sized" may
  anchor the grill toward confirming that framing. It is advisory by rule, but nothing enforces
  the assessor's independence from it — S2 and the pre-screen are the same session.
- **Sequential minting (v1) serialises everything.** A charter with eight slices runs eight
  framing→close cycles end to end. The `needs:` field makes v2 cheap, but until then a large
  charter's wall-clock is the sum of its slices, not the longest chain.
- **Rejection can be abused as a scope-dodge.** `not-now` is the honest label for "we decided
  against it", but it is also the easiest way to make an awkward requirement disappear while
  looking rigorous. The guard is that `not-now` *must* produce an `NG`/`BND` with a deferral
  target — but nothing verifies the deferral target is real. Watch the ratio of `not-now` to
  other reasons.
- **A charter is the easiest artifact in this system to fake.** Its checks verify slice *shape*,
  not whether the thesis is any good — no mechanical check can. Its only real quality control is
  the human bet at HG0 and the honesty of the bet log. Treat a high charter-health number with
  more suspicion than any other score here.
- **Appetite has no enforcement.** Nothing stops slices being added past the declared bound
  except the re-bet review. If `review_after` is set far out, a charter can drift for a long time
  while every individual item still scores well.
- **The escalation threshold (§7) is unvalidated.** The five conditions are reasoned, not
  measured; the >2 `COMP` and >1 `P` bounds in particular are guesses that should be retuned once
  real asks have been run through them.
- **Nothing here is validated end-to-end.** The existing system is validated through
  `frame → close` on a pilot repo; this contract has not been run once — including the human
  budget of ~3 touches, which is a design target, not a measurement.
