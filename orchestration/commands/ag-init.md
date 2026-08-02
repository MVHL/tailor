---
description: Onboard the current repo to the orchestration system (CLAUDE.md protocol, .orchestration/ scaffold, glossary, adapter).
argument-hint: (run inside the target repo; no args)
---

One-time setup so this repo's Claude Code sessions act as the Conductor.

Source of the orchestration assets: `${ORCH_HOME:-/Users/minh.le/WORK/tailor/orchestration}`.

Do the following:

1. Confirm we're at a git repo root (`git rev-parse --show-toplevel`). If not, stop and ask.
2. Create the scaffold:
   - `.orchestration/{runs,worktrees,bin}/`
   - copy `$ORCH_HOME/templates/{glossary.md,graph.md}` → `.orchestration/`
   - copy `$ORCH_HOME/templates/index.md` → `.orchestration/runs/index.md`
   - copy `$ORCH_HOME/bin/agy-run.sh` → `.orchestration/bin/agy-run.sh` (chmod +x) so the
     repo is self-contained and the exact adapter is versioned with the records.
3. Install the protocol (idempotent): the template begins with the marker
   `<!-- ORCHESTRATION PROTOCOL`. If `CLAUDE.md` does not exist, copy the template. If it
   exists and already contains that marker, **skip** (already onboarded) — say so. If it
   exists without the marker, **append** the protocol block (marker included) rather than
   clobbering; tell the user what you added. Also skip any scaffold file in step 2 that
   already exists, so re-running never overwrites live records.
4. Seed the glossary: use the `ubiquitous-language` skill to draft `.orchestration/glossary.md`
   from the codebase (real terms + a first pass at `COMP` components). Mark it "draft — curate".
5. Add `.orchestration/worktrees/` to `.gitignore` (transient worktrees shouldn't be committed;
   runs/ and the rest ARE committed — they're the audit trail).
6. Stage and show the diff; ask the user to confirm before committing.

Report what was created and the next step (`/ag-run "<idea>"`).
