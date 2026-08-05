# Brief for agy — <N>.<M> · iteration <i>

<!-- DERIVED ARTIFACT: mechanical assembly of story + TP + IP. No new judgment goes in here,
     and it carries no score of its own. If you find yourself deciding something while
     writing this brief, that decision belongs upstream in the story or the IP. -->

You are the implementer. Build exactly what makes the Test Plan pass — nothing more.
Work only inside this workspace. Do **NOT** merge, push, or delete branches.

## Ubiquitous language

<paste the relevant glossary terms + COMP definitions so agy uses the right words>

## Problem & requirements — context, do NOT re-scope

- `<N>#P1` — <problem>
- `R1` — <requirement>   `solves: <N>#P1`
- **Non-goals (do not build):** `NG1` — <excluded>

## Acceptance criteria — the definition of done

- `AC1` — <observable pass/fail condition>   `covers: R1`
- `AC2` — <…>

## Test Plan — MAKE THESE PASS (TDD)

These tests **already exist in the repo and currently FAIL**. Your job is to make them pass by
implementing real behavior.

<paste the TP.md test list>

```bash
<the single run command>
```

## Implementation Plan — how to build it

<paste the IP.md approach, IM steps, and sequencing>

### Reuse — do NOT reinvent these

<paste the IP.md reuse list with paths>

### Inherited constraints

<paste the charter's cross-cutting constraints, if this task came from a slice>

## Rules

- Make the failing tests pass. **Do not weaken, skip, or delete a test** to make it pass.
- Do not fabricate output to satisfy an assertion. A test that checks a transformation must be
  satisfied by real logic against the literal fixture data — a dummy marker of the right shape is
  treated as a hard failure, not a shortcut.
- Reuse the utilities named above; match the surrounding code style.
- Introduce no new framework, runner, or dependency.
- Stay inside the named `COMP`; do not touch the areas listed as off-limits.
- Commit referencing the realized ids, e.g. `feat: <desc> (AC2, IM1)`.
- When done, summarize what you changed and which `AC` are now satisfied.

<!-- ── ITERATION BRIEFS ONLY (iteration ≥ 2) ─────────────────────────────────
     Replace the sections above with a PRECISE fix instruction. Name the failing
     test, the file, and the gap — and paste the ACTUAL diff and failing output
     rather than describing them.

     If the fix is "restore prior behavior", attach the real prior commit as
     ground truth (`git show <sha> -- <file>`). Asking for a re-derivation from
     a prose description turns a restore into a fresh implementation attempt,
     which has introduced new bugs the working code never had.
     ───────────────────────────────────────────────────────────────────────── -->

## Fix required — iteration <i>

- **Failing:** `<test name>` in `<file>` → <the actual assertion failure>
- **Gap:** <what the current implementation does vs. what `AC#` requires>
- **Do not** change the test. Change the implementation.

```
<paste the actual failing output>
```
