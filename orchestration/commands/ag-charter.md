---
description: S0/HG0 — author a charter for an ask bigger than one epic (thesis, boundaries, appetite, ranked unknowns, ordered slices), mint slices into PRPs one at a time, or run the re-bet review.
argument-hint: "\"<oversized ask>\"  |  <C-id> --mint <SL#>  |  <C-id> --review"
---

Input: **$ARGUMENTS**

Invoke the **ag-charter** skill. Three modes:

## Author (`/ag-charter "<ask>"`)

Only when the ask genuinely exceeds one epic — judged by the §7 escalation test *after* Discovery,
not by how the ask was phrased. If it doesn't escalate, route to `/ag-frame` instead.

Write `charters/C<n>/charter-C<n>.md` from `templates/charter.md` + `decisions.md`
(`level: charter`): thesis · outcome signals · `BND` · **appetite** · ranked `UNK` · ordered `SL`
(each with a problem hypothesis, `reduces: UNK#`, optional `needs:`) · cross-cutting constraints ·
capability map (reference only).

Then run the exit check — appetite and `review_after` declared, ≥1 `BND`, every `SL` vertical and
hypothesized, `SL1` reduces `UNK1`, `needs:` acyclic, over-appetite slices cut to `BND` — and
**present the bet to the human. STOP there.** HG0 is never self-approvable: confidence cannot
substitute for a bet, because the uncertainty *is* the bet.

On approval: `status: canonical`, stamp `approved_by`/`approved_at`, set `review_after`, log a `DEC`
with `Kind: bet`, and add the charter row to `graph.md`.

## Mint (`/ag-charter <C-id> --mint <SL#>`)

A slice becomes a real PRP **only when picked up**. Eligible when every `needs:` is closed — and
until `UNK1` is reduced, **only `SL1` is mintable**.

Create the child container with `charter: C<n>` and `slice: C<n>#SL<m>`, seeded with the slice
hypothesis as raw intake text plus the inherited constraints. The charter's `ASK` is **context, not
evidence** — the child still gathers its own `SIG`. Set the slice `state: in-flight`, record
`minted:`, update `graph.md`, then hand to `/ag-frame`.

**v1 mints one slice at a time**, sequentially. Do not fan out yet — each slice's outcome should be
read before the next starts, which is what keeps the bet log meaningful.

## Re-bet (`/ag-charter <C-id> --review`)

Read the bet log, recompute `appetite_burn`, and present to the human: **continue** · **amend**
(reorder, re-cut, adjust appetite) · **invalidate**. Give a recommendation with the evidence.

On `invalidated`: drop unminted `SL`, decide explicitly what happens to in-flight children, log a
`DEC`. On continue: set the next `review_after`.

**Never skip a due re-bet because the slices are all green** — well-framed, cleanly-shipped slices
are exactly what a losing bet looks like from the inside.

---

Report: the charter path, appetite, `UNK` ranking, slice order, what `SL1` would prove, and what you
need from the human. State plainly that a charter's checks verify slice **shape**, not whether the
thesis is any good.
