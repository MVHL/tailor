# Navigation graph — bet ↔ spec ↔ code ↔ run

The traversable map an agent reads to answer: *which `AC` is uncovered? which file implements
`R2`? which slice is this epic under? which run touched this component? why was this decided?*
Not a database — linked, append-only items. Keep it current as items close.

## Charters → epics (the mutable link)

The charter→epic link lives in each epic's frontmatter (`charter: C3`); this table is the
readable index of it. Re-cutting an initiative edits **this table and the frontmatter** — never
an id.

| `C` | Charter | Appetite | Slices (state) | Epics | Status |
|-----|---------|----------|----------------|-------|--------|
| C1 | <name of the bet> | <1 quarter> | SL1 done · SL2 in-flight · SL3 hypothesis | 24, 25 | canonical / invalidated |

## Epics → tasks

| Container | Type | Title | Charter · Slice | Tasks | Status |
|-----------|------|-------|-----------------|-------|--------|
| 24 | epic | <name> | C1 · SL2 | 24.1, 24.2 | framing / building / done |
| 25 | bug (collapsed) | <name> | — | 25.1 | done |

## Features

| `FEAT` | Feature | Requirements | Status |
|--------|---------|--------------|--------|
| FEAT1 | <name> | 24#R1, 24#R3 | framing / building / done |

## Components → code

| `COMP` | Component | Code home | Realizing runs |
|--------|-----------|-----------|----------------|
| COMP1 | <name> | <dir/module> | 24.1, 24.2 |

## Spec → code anchors (filled from agy's diff at S8)

| `AC` / `IM` | Realized by | `touches:` (file#symbol) |
|-------------|-------------|--------------------------|
| 24.1#AC1 | 24.1 | <path#symbol> |

## Stale watch

Editing a canonical `P` flips every artifact that references it to `stale`. Record the cascade
here when it happens, so nothing silently ships against a changed problem.

| Changed item | When | Dependents marked stale | Re-blessed |
|--------------|------|-------------------------|------------|
| 24#P1 | <UTC> | 24.1, 24.2 | 24.1 ✓ · 24.2 pending |

## Rejected — kept on the record

A rejected item is never deleted: it is the answer when the same ask returns. A rejected `P` does
**not** invalidate its `SIG` — the signal returns to the unaddressed pool below.

| Container | Reason | Stage | Became | `DEC` |
|-----------|--------|-------|--------|-------|
| 26 | not-now | HG1 | 24#NG3 (deferred to Q3) | 24#DEC4 |

## Unaddressed signals

`SIG` with no live `P` — either never triaged, or its `P` was rejected. Visible on purpose: this
is the backlog of real evidence nobody has acted on.

| `SIG` | From | Date | Why unaddressed |
|-------|------|------|-----------------|
| 26#SIG1 | <source> | <date> | P rejected `infeasible`; may resurface with different `R` |

## Decisions

| `DEC` | Level | Decision | Links | Where |
|-------|-------|----------|-------|-------|
| DEC1 | epic | <one line> | resolves 24#OQ1 | 24 |
