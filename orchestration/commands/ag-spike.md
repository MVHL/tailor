---
description: S2b — time-boxed investigation that surfaces dependencies (D) and risks (RK) before requirements exist, and can reject a problem as infeasible.
argument-hint: "<container-id>  [question to answer]"
---

Spike **$ARGUMENTS**. Invoke the **ag-spike** skill.

Optional by design — most problems are already understood and skip straight to S3/S4. Run this only
when the problem touches legacy or undocumented behavior, feasibility is genuinely unknown, or a
charter slice exists specifically to reduce a ranked `UNK`.

1. **State the question and the box** — one sentence on what must be answered, plus a declared time
   or effort bound. An unbounded spike is a rewrite in disguise.
2. **Investigate** — read code, run things, check external systems; spawn `Explore` sub-agents for
   breadth. Throwaway scratch code goes in the scratchpad, never in the repo.
3. Write `epics/<n>/spike-<n>.md`:
   - **`D`** — `<factor>  affects: P#  owner: <who outside this team>`. No named external owner means
     it is a task, not a dependency.
   - **`RK`** — `<risk>  threatens: P#  likelihood: <…>  impact: <…>`. Both fields required, or the
     risk cannot be weighed against scope.
4. **Answer the question explicitly** — including "we still don't know", with what would be needed
   to find out and an `OQ` opened.
5. **Feed forward** — say how each `D`/`RK` should shape scope at S3 (a `D` usually **constrains** an
   `R`; an `RK` may **justify** an `NG`). Do not decide that here; S3 does, and G1 checks it was
   visibly factored in.

**The rejection exit.** Propose `rejection_reason: infeasible` when it cannot be built as framed, is
architecturally incompatible in a way no `R` works around, or costs wildly beyond any plausible
appetite. You propose; the human confirms. Record the evidence, not just the conclusion.

Rejecting here is **cheap and healthy** — before any `AC`, test, or plan exists. The same
realization at G3 costs the whole chain. And a rejected `P` does **not** invalidate its `SIG`: move
the signal to the unaddressed pool in `graph.md`.

If this spike is a charter slice reducing `UNK1`, say whether that unknown is now reduced, unchanged,
or worse than assumed — `/ag-close` carries it into the bet log.

Report: the question, the answer, each `D`/`RK` with its up-link, how they should shape scope, and
either "proceed to S3" or a rejection proposal with evidence.
