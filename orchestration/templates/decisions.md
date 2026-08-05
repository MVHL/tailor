---
id:      <N>                # C<n> at charter level · <N> at epic level · <N>.<M> at task level
type:    decisions
level:   epic               # charter | epic | task
---

# Decisions — <ID>

Append-only. Every human exchange, every non-obvious call, every waiver. This is the auditable
**"why"**.

> **A `DEC` lives at the level whose scope it *binds*** — not the level where it happened to
> surface. A decision that constrains every slice belongs to the **charter**, even if it was
> discovered while building slice 3. Otherwise charter-level constraints get buried in a task
> directory where no sibling will ever read them.

| Level | What belongs here |
|-------|-------------------|
| charter | bets, re-bets, slice cuts, appetite calls, cross-cutting architecture constraints |
| epic | HG1 scope approvals, problem interpretation, `not-now` rejections, G1 waivers |
| task | planning calls, agy iteration decisions, Conductor direct edits, HG2 merge approval |

**A `DEC` is never edited.** A reversed decision is a *new* `DEC` carrying `supersedes: DEC#`.

---

## DEC1 — <short title>

- **When:** <UTC ISO8601>
- **Kind:** `approval` | `rejection` | `waiver` | `scope-call` | `bet` | `direct-edit` | `other`
- **Trigger:** <why a decision was needed — ambiguous scope · conflicting requirements ·
  missing AC · irreversible action · gate budget exhausted · re-bet due · finding waived>
- **Question asked:** <verbatim, if a human was asked>
- **Answer / decision:** <what was decided>
- **Decided by:** <human name | Conductor (auto)>
- **Links:** `resolves: OQ#` · `accepts: ASM#` · `constrains: R#` · `waives: F#` ·
  `supersedes: DEC#`

---

## Conventions

- **Approvals.** HG0, HG1, and HG2 each produce a `DEC` with `Kind: approval`. An approval that
  leaves no record is not an approval — the board cannot show "waiting on human" and nobody can
  audit who said yes to the scope.
- **Rejections.** A rejection `DEC` records the `rejection_reason`. A `not-now` rejection **must**
  also name the `NG`/`BND` it became, with a deferral target.
- **Auto-approvals.** A self-approved HG1 (WORKFLOW §5) is logged with
  `Decided by: Conductor (auto)` and **lists the five conditions that were met**. These show
  distinctly on the board so they stay spot-checkable.
- **Direct edits.** A Conductor edit to application code is logged **at the moment it is made**,
  not retroactively. If the edit turns out to be wrong, that is a *second* `DEC`, also logged
  immediately — never folded silently into the first.
- **Waivers.** Record which finding, and why it cannot be fixed now. Waivers are counted and
  deduct from the artifact score, so they stay honest.
