---
name: ag-charter
description: Author a charter for an ask bigger than one epic — thesis, boundaries, appetite, ranked unknowns, and ordered vertical slices — then mint slices into PRPs one at a time and run the re-bet review. Use when an ask spans multiple problems or components ("build the platform", "rebuild reporting"), when a PRP escalates past the size threshold, or when asked to "charter", "scope an initiative", or "break this into slices".
---

# ag-charter — S0 + HG0: the bet above the PRP

You are Role A at portfolio scope. This is `WORKFLOW.md` **S0 / HG0**; read §4 (per-step notes),
§6 (charter row), §7 (escalation), and §11 (minting) before writing.

## The one rule that decides whether this skill applies

> **A charter is a bet, not a problem** (R10).

It holds a thesis, boundaries, an appetite, ranked unknowns, and ordered slices. It **never**
holds `P`/`R`/`NG`/`AC`. Stretching a PRP to hold a platform-sized ask yields a `P` so abstract
that every downstream check passes *vacuously* — worse than having no checks at all.

If you find yourself writing a problem statement into the charter, stop: either the ask was not
charter-sized (go to `ag-frame`), or that problem belongs in a slice.

## When to escalate (WORKFLOW §7)

Judged **by the outcome of Discovery**, never by how the ask was phrased. *"Just add SSO"* can be
a quarter of work; *"rebuild the reporting platform"* can be one config change. Escalate when,
after S2, **any** hold:

- the ask yields **>1 `P`** with no single measurable impact between them
- **no single `AC` set** could demonstrate the ask is satisfied
- it spans **>2 `COMP`**
- it needs **sequencing decisions** — parts only make sense after others land
- its `NG` set is doing the work of a roadmap rather than bounding one problem

Escalation is **agent-proposed, human-confirmed**. A pre-screen may *propose* the charter route
before the grill starts so an obviously platform-sized ask isn't grilled as one problem — but it
is advisory, and S2's evidence overrules it.

## Inputs

The oversized ask; `.orchestration/glossary.md`; `graph.md` (existing `COMP` and charters); an
in-progress `prp-<n>.md` if this is a promotion.

## Procedure

### 1. Allocate or promote

- **New:** take the next `C<n>` from `charters/`. Create `charters/C<n>/` with
  `charter-C<n>.md` (from `templates/charter.md`) and `decisions.md` (`level: charter`).
- **Promotion** (a PRP outgrew itself): keep the epic's container id, carry `SIG`/`ASK` over
  verbatim, and turn the draft `P`s into `UNK`/`SL` hypotheses. Tombstone the PRP with a pointer.
- **Retroactive** (existing epics turn out to be one bet): write the charter, then set
  `charter: C<n>` in each epic's frontmatter and add the row to `graph.md`. **No renumbering** —
  that is what the frontmatter link buys.

### 2. Write the thesis and outcome signals

**Thesis:** what becomes true if this succeeds — a claim about the world, one paragraph.
**Outcome signals:** how you would know the bet paid off. Leading indicators, *not* `AC` — outcome
metrics, not pass/fail checks. Each with a current value and what would count as success.

### 3. Bound it — `BND` and appetite

**`BND`:** what this charter explicitly is *not*. The charter-level analogue of `NG`.

**Appetite:** a declared bound (a time box, or a slice count) and an **input**, never an estimate
you produce. When the slices exceed it you **cut slices** — they become `BND` — rather than
extending the bound. A charter with no declared appetite grows forever.

### 4. Rank the unknowns — `UNK`

The risky assumptions, most dangerous first. This ranking is the whole mechanism behind
"sequence by uncertainty": without it, slice order defaults to whatever is easiest.

Grill the human here, not just yourself: *what would have to be true for this to work? what would
make us abandon it? what do we least know?*

### 5. Slice it — `SL`

Each `SL` is a **thin end-to-end outcome someone can evaluate**, with:

- a one-line **problem hypothesis** (it becomes the child's raw intake text)
- `reduces: UNK#`
- `needs: SL#` — only for a *genuine* sequencing constraint, and acyclic
- `state: hypothesis`

**Decompose by outcome, not by capability.** Splitting into auth / billing / reporting means three
things built before anything is usable. A slice that delivers only a layer ("the data model",
"the auth service") is not a slice — reject it and re-cut.

**`SL1` must reduce `UNK1`** — the biggest unknown, not the easiest layer. If the bet is wrong you
want to know at slice 1, not slice 7. For a genuinely novel ask, the right `SL1` is often a
**walking skeleton or a prototype** rather than a feature: route it through `ag-spike` or the
`prototype` skill.

Record the **capability map** separately, as reference only. It answers *where code lives*
(`COMP` in `graph.md`); `SL` answers *what we build next*. Conflating the two is how a charter
silently becomes a horizontal plan.

### 6. Cross-cutting constraints

Architecture, tech, compliance — anything inherited by every child. These must be **cited** in
each child's `IP.md`, and G2 checks that they were.

### 7. Exit check (mechanical — run before HG0)

Refuse to present the charter if any fail:

- appetite declared · `review_after` set · ≥1 `BND`
- every `SL` has a hypothesis **and** `reduces: UNK#`
- every `SL` is vertical (an evaluable outcome, not a layer)
- `UNK` ranked, and `SL1` reduces the top one
- the `needs:` graph is acyclic
- slices beyond the appetite explicitly cut to `BND`

### 8. HG0 — the human makes the bet

Present: thesis · appetite · `UNK` ranking · `SL` order · what `SL1` would prove. The exit check
verified slice *shape*; the human decides *direction* (R9). **Never** self-approve HG0 — confidence
cannot substitute for a bet, because the uncertainty is the bet.

On approval set `status: canonical`, stamp `approved_by`/`approved_at`, set `review_after`, and log
a `DEC` with `Kind: bet`.

## Minting — `--mint <SL#>`

A `SL` becomes a real PRP **only when picked up** (R11). Pre-writing every child PRP is waterfall
in this contract's vocabulary.

1. **Eligibility.** A `SL` is mintable when every `needs:` is closed — and until `UNK1` is
   reduced, **only `SL1` is mintable at all**.
2. Take the next container id, create `epics/<n>/` (or a collapsed `runs/<n>.1/`) with
   `prp-<n>.md` from the template, setting `charter: C<n>` and `slice: C<n>#SL<m>`.
3. Seed it: the slice hypothesis as raw intake text, plus the inherited constraints. **The
   charter's `ASK` is context, not evidence** — the child still gathers its own `SIG`.
4. Set the `SL` to `state: in-flight`, `minted: <n>`. Update `graph.md`.
5. Hand off to `ag-frame`. The child then runs the ordinary chain with **no** charter-specific
   variation.

**v1: mint one at a time**, sequentially, until the list is done — it keeps the bet log meaningful
because each slice's outcome is read before the next starts. `needs:` is recorded from day one so
parallel minting later is a scheduler change, not a schema migration.

## Re-bet — `--review`

Triggered when `review_after` is reached (`/ag-close` halts and requests it — it never mints past
a due re-bet).

1. Read the **bet log**: did the thesis hold across the slices so far?
2. Recompute `appetite_burn` (slices minted ÷ appetite).
3. Present to the human with a recommendation: **continue** · **amend** (reorder, re-cut, adjust
   appetite) · **invalidate**.
4. On `invalidated`: unminted `SL` are dropped; in-flight children stop or finish by explicit
   decision. Log a `DEC`; set the new `review_after` if continuing.

**A charter with no scheduled re-bet is how zombie initiatives survive.** Never skip it because
the slices are all green — well-framed, cleanly-shipped slices are exactly what a losing bet looks
like from the inside.

## Honest limits to state when you present a charter

- Its checks verify slice **shape**, not whether the thesis is any good — no mechanical check can.
  Its only real quality control is the human bet and the honesty of the bet log.
- **Appetite has no enforcement** between re-bets. If `review_after` is far out, the charter can
  drift a long way while every individual item still scores well.
