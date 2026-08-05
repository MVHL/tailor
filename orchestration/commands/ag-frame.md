---
description: Phase A — intake, discovery grill, specification, and refinement. Produces SIG/ASK/P, then canonical R/NG/AC. Halts at HG1 for scope approval.
argument-hint: "<idea, ask, bug report>  OR  <container-id> to continue framing"
---

Frame: **$ARGUMENTS**

Invoke the **ag-frame** skill. This drives `WORKFLOW.md` **S1 → S2 → (S2b) → S3 → S4**, which may
share one session (the single R4 exception).

1. **S1 Intake** — allocate the container id; create `epics/<n>/` (or `runs/<n>.1/` if collapsed)
   with `prp-<n>.md` and `decisions.md`. Capture `SIG` **verbatim** with source + date, then `ASK`
   as a labelled solution hypothesis. Never copy an `ASK` into an `R`.
2. **S2 Discovery** — draft `P` with `evidence:`, then grill against the **eleven-aspect coverage
   checklist**, marking each `answered` · `assumed` · `n/a + reason`. Log every Q&A as a `DEC`.
   Compute `discovery_coverage`.
   - If the human is unavailable: mark `assumed`, open an `ASM`, and **proceed** — they resolve the
     batch at HG1. But an `ASM` on scope aspect 5 or 6 will block HG1.
   - **Propose rejection** if the problem dissolves (`dissolved`). **Propose escalation** to
     `/ag-charter` if the §7 conditions hold. Both are human-confirmed.
3. **S2b Spike** *(optional)* — only if feasibility is unknown or the problem touches legacy or
   undocumented behavior. Route to `/ag-spike`.
4. **HG1** — run the S3 exit check, then **STOP** and route to `/ag-approve <id>`. Do not proceed
   into S4 on unapproved scope.
5. **S3 Specification** — canonical `R` (`solves: P#`) and `NG` (**`excludes: P#`** + deferral
   target), draft `AC` per requirement, `FEAT`/`COMP` tags.
6. **S4 Refinement** — slice into `story-<n>.<m>.md` with the `R`/`NG` subset and **canonical `AC`**.
   `P` is never re-authored: reference the parent and embed a read-only copy, or own it locally.
   One session may emit all sibling stories.

**Do not run the assessor pass yourself.** G1 (`/ag-review-framing`) is an independent cold assessor
that has not seen the grill — that independence is the entire reason it is a separate gate.

Report: artifacts written, `discovery_coverage` with the open-assumption count, `ASM`/`OQ` raised,
and the next step. Stop and ask the human on genuine scope decisions; log each as a `DEC`.
