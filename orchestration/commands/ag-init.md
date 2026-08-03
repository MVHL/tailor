---
description: Onboard the current repo to the orchestration system (CLAUDE.md protocol, .orchestration/ scaffold, glossary, adapter).
argument-hint: (run inside the target repo; no args)
---

One-time setup so this repo's Claude Code sessions act as the Conductor.

**Resolve the orchestration source (no hardcoded paths).** The `/ag-init` command is itself
a symlink into the source tree, so derive `$ORCH_HOME` from it — this works wherever the
source lives and never points at a stale path:
```bash
ORCH_HOME="${ORCH_HOME:-$(cd "$(dirname "$(readlink ~/.claude/commands/ag-init.md)")/.." && pwd)}"
```
If that resolves to an empty/nonexistent dir (e.g. the command wasn't installed via symlink),
stop and tell the user to set `ORCH_HOME` to the orchestration source directory.

Do the following:

1. Confirm we're at a git repo root (`git rev-parse --show-toplevel`). If not, stop and ask.
2. Create the scaffold:
   - `.orchestration/{runs,worktrees,bin}/`
   - copy `$ORCH_HOME/templates/{glossary.md,graph.md}` → `.orchestration/`
   - copy `$ORCH_HOME/templates/index.md` → `.orchestration/runs/index.md`
   - copy `$ORCH_HOME/bin/agy-run.sh` + `$ORCH_HOME/bin/ag-agent.sh` +
     `$ORCH_HOME/bin/ag-agent-hook.py` → `.orchestration/bin/` (chmod +x) so the repo is
     self-contained and the exact adapters are versioned with the records. `agy-run.sh`
     delegates to agy (and writes the live `running.json` marker); `ag-agent.sh` records
     Claude sub-agent breadcrumbs by hand; `ag-agent-hook.py` records them automatically
     (see the hook install below).
   - copy `$ORCH_HOME/bin/ag-dashboard.py` + `$ORCH_HOME/templates/dashboard.html` →
     `.orchestration/bin/` so `/ag-board` works from inside the repo.
3. Install the protocol (idempotent): the template begins with the marker
   `<!-- ORCHESTRATION PROTOCOL`. If `CLAUDE.md` does not exist, copy the template. If it
   exists and already contains that marker, **skip** (already onboarded) — say so. If it
   exists without the marker, **append** the protocol block (marker included) rather than
   clobbering; tell the user what you added. Also skip any scaffold file in step 2 that
   already exists, so re-running never overwrites live records.
4. Seed the glossary: use the `ubiquitous-language` skill to draft `.orchestration/glossary.md`
   from the codebase (real terms + a first pass at `COMP` components). Mark it "draft — curate".
5. **Install the sub-agent hook (automatic Gap-B capture):** register `ag-agent-hook.py` on
   the `Agent` tool so every Claude sub-agent spawn self-records to `.orchestration/agents/`
   and shows on the board — no manual `ag-agent.sh` call needed. Merge this into
   `.claude/settings.json` (create the file if missing; if a `hooks` block exists, add these
   entries without clobbering existing hooks):
   ```json
   {
     "hooks": {
       "PreToolUse":  [ { "matcher": "Agent", "hooks": [ { "type": "command",
         "command": "python3 \"$CLAUDE_PROJECT_DIR/.orchestration/bin/ag-agent-hook.py\"" } ] } ],
       "PostToolUse": [ { "matcher": "Agent", "hooks": [ { "type": "command",
         "command": "python3 \"$CLAUDE_PROJECT_DIR/.orchestration/bin/ag-agent-hook.py\"" } ] } ]
     }
   }
   ```
   The hook no-ops outside onboarded repos and never blocks the session. The file watcher
   normally picks it up within seconds; if sub-agents still don't appear, the user should
   restart the session (or check `/hooks`). Tell the user the hook was installed.
7. Add `.orchestration/worktrees/` to `.gitignore` (transient worktrees shouldn't be committed;
   runs/ and the rest ARE committed — they're the audit trail).
8. **Register for the dashboard:** append this repo's absolute root (from
   `git rev-parse --show-toplevel`) to `~/.claude/orchestration-repos.txt` (create the file if
   needed; skip if the path is already listed). This is what lets `/ag-board` show every
   onboarded repo on one board without re-listing them.
9. Stage and show the diff; ask the user to confirm before committing.

Report what was created and the next step (`/ag-run "<idea>"`).
