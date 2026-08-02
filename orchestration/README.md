# orchestration — Claude Code as Conductor, agy as Implementer

A thin, Claude-Code-native layer that lets Claude Code **lead** software work (frame →
plan → review) and **delegate implementation** to the Antigravity CLI (`agy`), keeping a
git-native audit trail of every task. No platform, no server — just skills, slash
commands, a shell adapter, and file conventions. See the full plan at
`~/.claude/plans/i-want-to-make-noble-pixel.md`.

## What's here (source of truth)

```
orchestration/
  bin/agy-run.sh        # the ONLY way agy is called: worktree-scoped, JSON output,
                        #   transcript capture, conversation continuity. Confirmed vs agy 1.1.9.
  skills/               # installed into ~/.claude/skills/ via symlink
    ag-frame/         #   grill signal→ask→problem into a canonical P/R/NG/AC spec
    ag-test-plan/     #   tests FIRST (TDD) — failing tests + run command
    ag-impl-plan/     #   approach/files/reuse/constraints for agy
    ag-delegate/      #   worktree + brief + adapter + bounded review loop
  commands/             # installed into ~/.claude/commands/ via symlink
    ag (master), ag-init, ag-frame, ag-plan, ag-delegate, ag-review, ag-close, ag-run
  templates/            # CLAUDE.md protocol + record scaffolds (spec/TP/IP/brief/RECORD/…)
```

Skills and commands are **symlinked** into `~/.claude/`, so this repo is the single source
of truth — edit here, it's live everywhere.

## Install (already done on this machine)

```bash
# skills
for s in ag-frame ag-test-plan ag-impl-plan ag-delegate; do
  ln -sfn "$PWD/skills/$s" ~/.claude/skills/$s; done
# commands
for c in ag ag-init ag-frame ag-plan ag-delegate ag-review ag-close ag-run; do
  ln -sfn "$PWD/commands/$c.md" ~/.claude/commands/$c.md; done
# adapter on PATH (convenience)
ln -sfn "$PWD/bin/agy-run.sh" ~/.local/bin/agy-run
```

`ag-init` reads assets from `$ORCH_HOME` (default this dir). Export `ORCH_HOME`
if you move it.

## Use

- **Onboard a repo (once):** `cd <repo>` → `/ag-init` → commit.
- **The one command to remember:** `/ag "<idea/PRP/bug>"` (new task) or
  `/ag <task-id>` (resume where it left off) or `/ag` (status overview).
  It detects the task's stage and runs the right next step through to done.
- **Step by step (power use):** `/ag-frame` → `/ag-plan <id>` → `/ag-delegate <id>` →
  `/ag-review <id>` → `/ag-close <id>`. (`/ag-run` = the linear full loop.)

## Scoring & analytics

Each closed task emits a `metrics` block into `RECORD.md` frontmatter (0–100 per step +
raw agy tokens/seconds) per `templates/scoring.md`. This powers first-pass rate, spec
health, cost/time per task, and review-burden analytics in the Phase-2 dashboard.

## Guarantees (the point of the system)

- **SDD** — nothing reaches agy without a canonical spec; the Definition-of-Ready gate blocks it.
- **TDD** — Test Plan authored before code; agy told to make failing tests pass; red→green verified.
- **DDD** — `.orchestration/glossary.md` is the ubiquitous language; `COMP` tags map spec→code.
- **Audit** — every task leaves `spec / TP / IP / brief / transcript / review / decisions /
  RECORD` under `.orchestration/runs/<id>/`, committed. RECORD always closes with
  **assumptions / discovered problems / possible bugs / open issues**.
- **Trust boundary** — the git diff + tests are the source of truth; agy's self-report is
  never trusted. The Conductor owns the merge; agy never merges or pushes.

## Status

- **Phase 0–1 (MVP): built and validated end-to-end** on a pilot repo (`frame → … → close`,
  red→green, RECORD written, worktree merged).
- **Phase 2 (next):** a single-file HTML dashboard reading `runs/*/RECORD.md` frontmatter —
  overview-first triage (what needs attention), drill into a run. Own layout, not a review clone.
- **Phase 3 (deferred):** Jira/GitLab MCP sync (needs OAuth), Slack I/O, voice, an agy
  MCP/bridge (only when concurrency or non-Claude triggers are needed), plugin packaging.

## Known limitations

- `ag-init` resolves assets via a machine-local `$ORCH_HOME` — not yet a portable
  plugin (Phase 3).
- agy iteration budget and model are chosen by the Conductor; no cost/token accounting yet.
- Verified against agy **v1.1.9**; CLI flags/JSON schema may drift — `agy-run.sh` extracts
  fields defensively.
