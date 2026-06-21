# Jira Item-Level Traceability — Convention Spec

> Companion to `jira-ticket-anatomy.html`. The HTML is the **visual explainer** (what good looks like).
> This doc is the **convention the team applies** (how to do it in real tickets).
>
> Core idea: decompose a ticket into atomic, tagged items across five layers, and express the
> links between them in plain text. **Humans read the tags; the AI agent does the tagging and
> maintenance.** No Jira plugin required.

---

## 1. The five layers

Every ticket of meaningful size decomposes into these layers. Each item gets a tag with a stable ID.

| Layer | Prefix | What it is | Answers |
|---|---|---|---|
| Problem | `P` | The user/business problem being solved | *Why* |
| Requirement | `R` | A capability the solution must provide | *What must be true* |
| Acceptance Criterion | `AC` | A specific, testable pass/fail condition | *How we know it's done* |
| Test | `T` | A test that verifies one or more ACs | *How we prove it* |
| Implementation | `im` | A concrete unit of work that builds it | *How we build it* |

Not every ticket needs all five. A small bug fix may be `P → AC → T`. Use judgment; the agent proposes, a human confirms.

---

## 2. Tag and link format

Tags are inline, plain-text, and human-skimmable. Links are expressed as a `(← parent-ids)` suffix.

```
[P1] Users can't redeem multiple promo codes in one order
  [R1] Support up to N codes per cart                 (← P1)
  [R3] Reject mutually-exclusive code combinations    (← P1, P2)
    [AC4] Two conflicting codes → clear error shown    (← R3)
      [T4]  test: conflicting codes are rejected        (← AC4)
      [im2] CartValidator.checkConflicts()              (← AC4)
```

Rules:
- **The ID is in square brackets**, at the start of the item: `[AC4]`.
- **Links point upward** to the item(s) this one derives from, in the `(← …)` suffix.
- Downward links (a requirement listing its ACs) are **not** written — they're derived by reading all the upward links. This keeps every link recorded in exactly one place, so it can't disagree with itself.
- The suffix line is **agent-regenerated**. Humans write the text; the agent maintains the `(← …)`.

---

## 3. The append-only ID rule (most important)

**IDs are assigned once and never reused or renumbered.**

- New item → next unused number for its prefix (`R5`, even if `R2` was deleted).
- Deleted item → leave a tombstone so its ID is never recycled and dangling links are visible:
  ```
  [R2] ~~Withdrawn: merged into R1~~   (retired 2026-06-21)
  ```
- Never "tidy up" numbering. `R1, R3, R5` with gaps is correct and intentional.

Why: every link references an ID. If `R3` silently becomes `R4` after an insert, every `(← R3)` now points at the wrong item — and the graph rots the same way hand-maintained matrices always have, just via the agent instead of a human. Stable IDs are what make automated maintenance trustworthy.

---

## 4. Where the tags live in the ticket

- Tags live in the **ticket body**, inside the existing sections (Problem Statement, Requirements, Acceptance Criteria, Test Plan, Implementation Plan).
- They do **not** go in Jira comments (transient) or in custom fields (needs tooling).
- PR links, commit hashes, and run-time discussion stay where they belong (dev panel / comments) — see the "Don't Dump These in the Body" panel in the HTML demo.

---

## 5. Two agent roles — keep them separate

The agent does two jobs with different failure modes. Run them as **separate passes**.

### Role A — Author / Maintainer
- Decomposes prose into tagged items; assigns IDs per the append-only rule.
- On change, regenerates the `(← …)` link suffixes and adds tombstones for removed items.
- **Never** renumbers existing IDs.

### Role B — Assessor (adversarial)
- Grades quality and coverage **against** the tags, and is allowed to **challenge the tags themselves**.
- Must not assume the structure is correct just because Role A produced it. (Otherwise "100% coverage" only means "the agent linked what it created.")
- Output is advisory findings for a human, not silent edits.

> Rule of thumb: Role A makes the graph; Role B tries to break it. Different prompts, ideally different runs.

---

## 6. What the Assessor checks (coverage rules)

| Check | Finding when violated |
|---|---|
| Orphan requirement | `R` with no `(← P…)` → requirement traces to no problem (scope creep) |
| Orphan implementation | `im` with no `(← …)` → work traces to no requirement (gold-plating) |
| Uncovered AC | `AC` with no `T` linking to it → untested acceptance criterion |
| Untestable AC | `AC` not phrased as a pass/fail condition → flag for rewrite |
| Bare requirement | `R` with no `AC` → requirement that can never be marked done |
| Dangling link | `(← R2)` where `R2` is a tombstone or missing → broken trace |

These are set operations over the tags, which is exactly why the structure makes the assessment **auditable**: every finding points at a specific ID a human can check.

---

## 7. When the agent runs (trigger points)

Drift happens between runs, so pick the moments the structure **must** be trustworthy:

- **On transition → In Progress** — Author pass: structure exists and is sound before work starts.
- **On transition → In Review** (or PR open) — Assessor pass: coverage and orphans checked before merge.

Avoid "continuously," which in practice means "never, reliably." Tie runs to gates that already exist in the workflow.

---

## 8. Division of labor

| | Human | AI agent |
|---|---|---|
| Write the substance (problem, requirements, ACs in prose) | ✅ | proposes drafts |
| Assign/maintain IDs and link suffixes | spot-checks | ✅ (heavy lifting) |
| Enforce append-only ID rule | — | ✅ |
| Grade coverage / surface gaps | reviews findings | ✅ (Assessor) |
| Final judgment on scope and "done" | ✅ | advises only |

The agent owns the bookkeeping. Humans own the meaning and the decisions.

---

## 9. Worked example (with a gap the Assessor would catch)

```
[P1] Users can't redeem multiple promo codes in one order
[P2] Conflicting codes silently apply the wrong discount

[R1] Support up to N codes per cart                  (← P1)
[R3] Reject mutually-exclusive code combinations     (← P1, P2)
[R4] Expired codes are rejected at apply time        (← P2)

[AC1] Up to N valid codes stack correctly            (← R1)
[AC4] Two conflicting codes → clear error shown      (← R3)
[AC5] Expired code → "code expired" error            (← R4)

[T1] test: N valid codes stack                       (← AC1)
[T4] test: conflicting codes rejected                (← AC4)

[im1] CartTotals.applyCodes()                        (← AC1)
[im2] CartValidator.checkConflicts()                 (← AC4)
[im3] CartValidator.checkExpiry()                    (← AC5)
```

Assessor findings:
- ⚠️ **AC5 is uncovered** — no `T` links to it (expiry has impl `im3` but no test).
- ✅ All requirements trace to a problem; all impl items trace to an AC.

---

## 10. What this is and isn't

- **Is:** requirements traceability (a long-proven practice in safety-critical software), applied at item level inside one ticket, with the maintenance cost shifted to an AI agent.
- **Isn't:** a new Jira feature, a plugin, or a novel concept. The only thing being invented is *this convention* + *the agent that keeps it honest*.
- **Limitation:** the value scales with ticket complexity and lifespan. For trivial, short-lived tickets the overhead won't pay off — apply it where decomposition genuinely helps.
