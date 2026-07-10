# Jira Trace Mechanic — how P1 / R1 / AC1 and the links actually live in Jira

The anatomy diagram shows IDs (`P1`, `R1`, `AC1`…) and relationships
(`solves`, `covers`, `deferred to`, `implements`). Native Jira has **none** of
these out of the box. This doc picks the cheapest mechanic that works on day one
and names what it does and doesn't give you.

## Decision: text-prefix IDs + native links for cross-ticket only

**Within one ticket** (P→R→AC→T→IM all in the same Story/Epic description):
represent IDs and up-links as **plain-text prefixes** in the description, exactly
as the templates show. No custom fields, no plugins.

```
- R2: Each code validated in <1s before checkout    solves: P1
- AC3: Validation completes <1s under normal load   covers: R2
```

**Across tickets** (Non-Goal deferred to a follow-up; Story delivers an Epic's
requirement; Bug blocks a Story): use **native Jira issue links**.

| Relationship                         | Mechanic                                  |
|--------------------------------------|-------------------------------------------|
| R / AC / T / IM within one ticket    | Text prefix in description (`solves:` …)  |
| Story → its parent Epic/PRD          | Native parent link / Epic link            |
| Non-Goal deferred to later work      | Issue link **"relates to"** → follow-up   |
| Bug blocks a Story                   | Issue link **"blocks" / "is blocked by"** |
| Tech ticket enables a Story          | Issue link **"relates to"**               |

## Why not custom fields or a plugin

| Option                          | Verdict | Reason |
|---------------------------------|---------|--------|
| **A. Text prefixes + native links** | ✅ Recommended | Zero config, works today, survives export, readable by humans and the framing skill. |
| B. Custom fields per artifact   | ❌ Not for the pilot | Needs Jira-admin work, per-project config, and still can't hold a *list* of IDs cleanly. |
| C. Labels (`P1`, `R1`)          | ❌ | Labels are flat and global — they pollute the whole instance and can't express "R2 solves P1". |
| D. Marketplace traceability app | ⏸ Later | Real coverage automation, but cost + admin approval. Revisit only if the pilot proves value. |

## What this mechanic gives you

- Full **human-readable** trace in one place, copy-pasteable, diffable.
- Cross-ticket navigation through Jira's normal link UI and the dev panel.
- A format the `jira-problem-framing` skill can parse to report coverage gaps
  (orphan requirements, bare requirements, untestable ACs).

## What it does NOT give you (limitations — be honest about these)

- **No automated enforcement.** Nothing stops someone writing `R5` with no
  `solves:`. The coverage check is a *gate you run* (DoR checklist, or the
  framing skill), not something Jira blocks on its own.
- **No clickable jump** from `AC3` to `R2` inside a description — they're text.
  Acceptable because they're co-located in one ticket.
- **IDs are per-ticket, not global.** `AC3` means "AC3 of this story." Don't try
  to make IDs unique across the whole project; scope them to their ticket.

## If/when you outgrow it

Trigger to revisit (Option D): the squad is reframing >X tickets/sprint and
manually running coverage checks is the bottleneck. Until then, text + links is
the lowest-friction choice and the easiest to abandon if the WoW doesn't stick.
