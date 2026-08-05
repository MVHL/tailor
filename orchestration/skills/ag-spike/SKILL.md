---
name: ag-spike
description: Run a time-boxed investigation on a framed problem to surface dependencies (D) and risks (RK) before requirements are written — and to reject the problem outright if it proves infeasible. Use when a problem touches legacy or undocumented behavior, when feasibility is genuinely unknown, or when asked to "spike", "investigate", or "check if this is even possible".
---

# ag-spike — S2b: reduce the unknown before scoping it

You are Role A investigating, not building. This is `WORKFLOW.md` **S2b** — an *optional* step.
Most problems are already well understood and skip straight from S2 to S3/S4.

**Run a spike only when** the problem touches legacy or undocumented behavior, feasibility is
genuinely unknown, or a charter slice exists specifically to reduce a ranked `UNK`.

## Inputs

`epics/<n>/prp-<n>.md` with `P` at canonical-candidate (S2 complete). The codebase. The glossary.
If this came from a charter slice, the `UNK#` it is meant to reduce.

## Output

`epics/<n>/spike-<n>.md` containing `D` and `RK` items — **or** a rejection proposal.

Nothing else. A spike does not write `R`, `NG`, or `AC`, and it does not write production code.

## Procedure

1. **State the question and the box.** One sentence on what this spike must answer, and a declared
   time or effort bound. An unbounded spike is a rewrite in disguise.
2. **Investigate.** Read the code, run things, check external systems. Spawn `Explore` sub-agents
   for breadth. Throwaway scratch code is fine — put it in the scratchpad, never in the repo.
3. **`D` — dependencies.** External factors the work depends on:
   `D1: <factor>  affects: P#  owner: <who outside this team>`. A `D` with no named external owner
   is not a dependency, it is a task.
4. **`RK` — risks.** Things that could undermine a solution:
   `RK1: <risk>  threatens: P#  likelihood: <low|med|high>  impact: <…>`. Both fields are required —
   a risk without them cannot be weighed against scope.
5. **Answer the question explicitly**, including when the answer is "we still don't know" — say what
   would be needed to find out, and open an `OQ`.
6. **Feed forward.** Say plainly how each `D`/`RK` should shape scope at S3: a `D` usually
   **constrains** an `R`; an `RK` may **justify** an `NG`. Do not decide that yourself — S3 does,
   and G1 checks that they were visibly factored in.

## The rejection exit

A spike is one of the three places an item may be **rejected**, and often the most valuable one —
this is what spikes are *for*. Propose rejection with `rejection_reason: infeasible` when:

- it cannot be built as framed;
- it is incompatible with the existing architecture in a way no `R` can work around;
- the cost is wildly beyond any plausible appetite.

You **propose**; the human confirms (`WORKFLOW` §5). Record the evidence, not the conclusion alone.

**A rejected `P` does not invalidate its `SIG`** — the signal returns to the unaddressed pool in
`graph.md` and may resurface with different requirements. Killing the problem does not mean the
evidence was wrong.

Rejecting here is **cheap and healthy**: it happens before any `AC`, test, or plan exists. A
rejection at S2b costs one investigation; the same realization at G3 costs the whole chain.

## Charter slices

If this spike is the slice reducing `UNK1`, its real output is an **answer to that unknown**. Say
whether `UNK1` is now reduced, unchanged, or worse than assumed — `/ag-close` carries that into the
bet log, and a charter whose slices keep being rejected at S2b has a wrong **thesis**, not wrong
slices.

## Then stop

Report: the question, the answer, each `D`/`RK` with its up-link, how they should shape scope, and
either "proceed to S3" or a rejection proposal with its evidence.
