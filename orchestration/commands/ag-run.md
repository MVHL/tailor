---
description: RETIRED — a single session no longer runs the whole loop. Use /ag "<ask>" to start, or /ag <id> --to <step> to chain explicitly.
argument-hint: "<idea, ask, or bug report>"
---

**`/ag-run` is retired.** One session running frame → plan → delegate → close is the exact behaviour
the step contract exists to remove: it produced a single record for nine steps, so no step could be
scored, attributed, or improved on its own (`WORKFLOW.md` R4).

For **$ARGUMENTS**, do this instead:

- **New ask:** `/ag "<the ask>"` — sizes it by evidence (not by wording), then advances one step at a
  time.
- **Resume:** `/ag <container-id>`.
- **Chain deliberately:** `/ag <id> --to <step>` — the only supported way to advance multiple steps,
  and it **still halts** at HG0, HG1, and HG2.

The human stops are not optional and cannot be chained through: **HG0** (the bet), **HG1** (the scope
triple `P` + `R` + `NG`), **HG2** (the merge). Everything between them loops until pass with no human
involvement, which is where the automation actually lives.

Tell the user this command is retired, then run `/ag` with their input.
