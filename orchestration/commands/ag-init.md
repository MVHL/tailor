---
description: Onboard the current repo to the orchestration system (CLAUDE.md protocol, .orchestration/ scaffold with charters/epics/runs, glossary, adapters, sub-agent hook, dashboard registration).
argument-hint: (run inside the target repo; no args)
---

One-time setup so this repo's Claude Code sessions act as the Conductor per `WORKFLOW.md`.

**Resolve the orchestration source (no hardcoded paths).** `/ag-init` is itself a symlink into the
source tree, so derive `$ORCH_HOME` from it — this works wherever the source lives and never points
at a stale path:
```bash
ORCH_HOME="${ORCH_HOME:-$(cd "$(dirname "$(readlink ~/.claude/commands/ag-init.md)")/.." && pwd)}"
```
If that resolves to an empty or nonexistent dir (the command wasn't installed via symlink), stop and
tell the user to set `ORCH_HOME` to the orchestration source directory.

Do the following. **Skip any file that already exists** so re-running never overwrites live records.

1. Confirm we're at a git repo root (`git rev-parse --show-toplevel`). If not, stop and ask.

2. **Scaffold** `.orchestration/`:
   - dirs: `charters/`, `epics/`, `runs/`, `worktrees/`, `agents/`, `bin/`
   - copy `$ORCH_HOME/templates/{glossary.md,graph.md}` → `.orchestration/`
   - copy `$ORCH_HOME/templates/index.md` → `.orchestration/runs/index.md`
   - copy the **artifact templates** → `.orchestration/templates/` so records are versioned against
     the skeletons that produced them:
     `charter.md prp.md prd.md story.md TP.md IP.md brief.md review.md decisions.md RECORD.md
      scoring.md`
   - copy `$ORCH_HOME/bin/{agy-run.sh,ag-agent.sh,ag-agent-hook.py}` → `.orchestration/bin/`
     (`chmod +x`) so the repo is self-contained and the exact adapters are versioned with the
     records. `agy-run.sh` delegates to agy and writes the live `running.json`; `ag-agent.sh` records
     Claude sub-agent breadcrumbs by hand; `ag-agent-hook.py` records them automatically.
   - copy `$ORCH_HOME/bin/ag-dashboard.py` + `$ORCH_HOME/templates/dashboard.html` →
     `.orchestration/bin/` so `/ag-board` works from inside the repo.
   - copy `$ORCH_HOME/WORKFLOW.md` → `.orchestration/WORKFLOW.md` — the contract must travel with the
     records, or a record can't be interpreted later without the source tree.

3. **Install the protocol** (idempotent). The template begins with the marker
   `<!-- ORCHESTRATION PROTOCOL`. If `CLAUDE.md` doesn't exist, copy the template. If it exists and
   already contains that marker, **skip** and say so. If it exists **without** the marker, **append**
   the protocol block (marker included) rather than clobbering, and tell the user what you added.

   If the repo has an **older** protocol block (one describing the 5-activity loop `Frame → Plan →
   Delegate → Review → Record`), say so explicitly and offer to replace that section — do not silently
   leave two contradictory protocols in one file.

4. **Seed the glossary** — use the `ubiquitous-language` skill to draft `.orchestration/glossary.md`
   from the codebase (real terms + a first pass at `COMP` components). Mark it "draft — curate".

5. **Install the sub-agent hook** so every Claude sub-agent spawn self-records to
   `.orchestration/agents/` and appears on the board. Merge into `.claude/settings.json` (create if
   missing; if a `hooks` block exists, add without clobbering):
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
   The hook no-ops outside onboarded repos and never blocks the session. The watcher normally picks it
   up within seconds; if sub-agents still don't appear, the user should restart the session. Tell them
   it was installed.

6. **Autonomy defaults.** Create `.orchestration/charters/.gitkeep` and seed
   `.orchestration/decisions.md` (repo level) with a `DEC` recording that **HG1 self-approval is
   OFF** and **HG2 auto-merge is OFF**. Both are opt-in and both need an explicit `DEC` to enable —
   writing the default down means enabling it later is a visible, auditable change rather than a
   quiet one.

7. **gitignore** — add `.orchestration/worktrees/` (transient). Everything else under
   `.orchestration/` **is** committed: it is the audit trail.

8. **Register for the dashboard** — append this repo's absolute root to
   `~/.claude/orchestration-repos.txt` (create if needed; skip if already listed). This is what lets
   `/ag-board` show every onboarded repo on one board.

9. Stage and show the diff; **ask the user to confirm before committing.**

Report what was created, that both autonomy dials are off, and the next step: `/ag "<your ask>"`.
