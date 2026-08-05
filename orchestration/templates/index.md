# Runs index

Running log of every orchestrated item in this repo — newest last. Mirrors the
`measurement-config` changelog convention: a scannable "what happened / why" table that is the
entry point to the per-item records. The board reads the artifact frontmatter behind these rows.

`Step` is the furthest step reached (`S1`…`S8`, or the gate it is sitting at). `Waiting` names the
human stop it is blocked on, if any — `HG0` / `HG1` / `HG2` — so an approval backlog never reads
as an engineering backlog.

| Item | Type | Title | Charter·Slice | Step | Status | Waiting | Framing | Output | Tests | Record |
|------|------|-------|---------------|------|--------|---------|---------|--------|-------|--------|
| 24.1 | story | <title> | C1·SL2 | S8 | done | — | 92 | 88 | pass | [record](./24.1/RECORD.md) |
| 24.2 | story | <title> | C1·SL2 | G2 | in-review | — | 78 | — | — | — |
| 25.1 | bug | <title> | — | HG1 | blocked | HG1 | 85 | — | — | — |
| 26.1 | story | <title> | — | S2 | rejected | — | — | — | — | — |

Rejected items stay listed — a rejection is the answer when the same ask returns, and it is
excluded from the score distributions rather than hidden.
