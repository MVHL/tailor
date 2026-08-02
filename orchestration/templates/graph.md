# Navigation graph — spec ↔ code ↔ run

The traversable map an agent reads to answer: *which AC is uncovered? which file
implements R2? which run touched this component? why was this decided?* Not a database —
just linked, append-only items. Keep it current as tasks close.

## Features

| `FEAT` | Feature | Requirements | Status |
|--------|---------|--------------|--------|
| FEAT1 | <name> | R1, R3 | <framing / building / done> |

## Components → code

| `COMP` | Component | Code home | Realizing runs |
|--------|-----------|-----------|----------------|
| COMP1 | <name> | <dir/module> | <task-ids> |

## Spec → code anchors (filled from agy's diff at close)

| `AC`/`IM` | Realized by run | `touches:` (file#symbol) |
|-----------|-----------------|--------------------------|
| AC1 | <task-id> | <path#symbol> |

## Decisions

| `DEC` | Decision | Links | Run |
|-------|----------|-------|-----|
| DEC1 | <one line> | resolves P1 | <task-id> |
