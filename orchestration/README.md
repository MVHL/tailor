# orchestration — Claude Code as Conductor, agy as Implementer

A thin, Claude-Code-native layer that lets Claude Code **lead** software work (charter → frame →
plan → gate) and **delegate implementation** to the Antigravity CLI (`agy`), keeping a git-native
audit trail of every artifact. No platform, no server — skills, slash commands, a shell adapter, and
file conventions.

**[WORKFLOW.md](WORKFLOW.md) is the contract.** Steps, gates, artifact registry, id scheme, sizing
rules, rejection paths, the autonomy dial, and dispatch. Where any skill, command, or the board
disagrees with it, WORKFLOW.md wins.

## The shape of it

Work is a chain of **steps over artifacts** — each step consumes a declared IN set and emits a
declared OUT set, so each one can be scored and improved on its own.

```
Phase 0  S0 Charter → ▓HG0 bet▓ → mint one slice ⟲ re-bet        (only for oversized asks)
Phase A  S1 Intake → S2 Discovery → (S2b Spike) → S3 Spec
                   → ▓HG1 scope: P+R+NG▓ → S4 Refinement → G1 ⟲
Phase B  S5 Test Plan → S6 Impl Plan → G2 Readiness ⟲
Phase C  S7 Implementation (agy) → G3 Code review ⟲ → ▓HG2 merge▓ → S8 Close
```

Three human stops (`HG0` · `HG1` · `HG2`); everything between them loops until pass with no human.
Three machine gates (`G1` · `G2` · `G3`), each an **independent cold assessor** — the author never
grades their own work. Rejection exits at S2 / S2b / HG1, agent-proposed and human-confirmed.

## What's here (source of truth)

```
orchestration/
  WORKFLOW.md           # THE CONTRACT — read this first
  bin/agy-run.sh        # the ONLY way agy is called: worktree-scoped, JSON output, transcript
                        #   capture, conversation continuity, live running.json marker
  bin/ag-agent.sh       # Claude sub-agent breadcrumbs → .orchestration/agents/ (manual)
  bin/ag-agent-hook.py  # the automatic path: a PreToolUse/PostToolUse hook on the Agent tool
  bin/ag-dashboard.py   # scanner + renderer: charter view · items × steps · open threads
  skills/
    ag-charter/         #   S0/HG0 — the bet: thesis, appetite, ranked unknowns, vertical slices
    ag-frame/           #   S1–S4 — intake, the coverage grill, spec, refinement
    ag-spike/           #   S2b — surface D/RK, or reject as infeasible
    ag-review-framing/  #   G1 — cold assessor over SIG/ASK/P/R/NG/AC
    ag-test-plan/       #   S5 — tests first, red captured
    ag-impl-plan/       #   S6 — approach, IM steps, reuse, inherited constraints
    ag-review-ready/    #   G2 — Definition of Ready
    ag-delegate/        #   S7 — worktree, brief, adapter (judgment happens at G3)
    ag-review-code/     #   G3 — objective checks + independent AC grading
  commands/             # ag (dispatch), ag-init, ag-charter, ag-approve, ag-frame, ag-spike,
                        #   ag-test-plan, ag-impl-plan, ag-review-framing, ag-review-ready,
                        #   ag-delegate, ag-review, ag-close, ag-board
                        #   (ag-plan and ag-run are retirement stubs that route to the above)
  templates/            # charter · prp · prd · story · TP · IP · brief · review · decisions ·
                        #   RECORD · graph · index · scoring · CLAUDE.md protocol · dashboard.html
```

Skills and commands are **symlinked** into `~/.claude/`, so this repo is the single source of
truth — edit here, it's live everywhere.

## Install

```bash
for s in ag-charter ag-frame ag-spike ag-review-framing ag-test-plan ag-impl-plan \
         ag-review-ready ag-delegate ag-review-code; do
  ln -sfn "$PWD/skills/$s" ~/.claude/skills/$s; done
for c in ag ag-init ag-charter ag-approve ag-frame ag-spike ag-test-plan ag-impl-plan \
         ag-review-framing ag-review-ready ag-delegate ag-review ag-close ag-board \
         ag-plan ag-run; do
  ln -sfn "$PWD/commands/$c.md" ~/.claude/commands/$c.md; done
ln -sfn "$PWD/bin/agy-run.sh" ~/.local/bin/agy-run
ln -sfn "$PWD/bin/ag-dashboard.py" ~/.local/bin/ag-dashboard
```

`ag-init` reads assets via `$ORCH_HOME` (derived from the `/ag-init` symlink; export it if you move
this tree).

## Use

- **Onboard a repo (once):** `cd <repo>` → `/ag-init` → commit.
- **The one command:** `/ag "<ask>"` (new — sized by evidence, not by wording), `/ag <id>` (resume,
  one step), `/ag` (status). It halts at every human gate, including under `--to <step>`.
- **Step by step:** `/ag-charter` · `/ag-frame` · `/ag-approve` · `/ag-review-framing` ·
  `/ag-test-plan` · `/ag-impl-plan` · `/ag-review-ready` · `/ag-delegate` · `/ag-review` ·
  `/ag-close`.

## Records

```
.orchestration/
  charters/C<n>/   charter-C<n>.md · decisions.md
  epics/<n>/       prp-<n>.md · prd-<n>.md · spike-<n>.md · decisions.md
  runs/<n>.<m>/    story|bug|tech-<n>.<m>.md · TP · IP · brief · review-{framing,readiness,code}
                   · transcript · decisions · RECORD   (+ transient running.json)
  graph.md · glossary.md · runs/index.md · agents/
```

Filenames carry the id; **frontmatter is truth**. `ASM`/`OQ` live inline in the artifact they
annotate; a `DEC` lives at the level whose scope it binds.

## Scoring

Derived, never asserted — see [templates/scoring.md](templates/scoring.md). **Artifact score**
(check ratios − findings) → **step score** → **framing / output / charter health**. The board
recomputes all of it from the files on every scan.

## Board (`/ag-board`)

```bash
ag-dashboard --registry ~/.claude/orchestration-repos.txt --out ~/.orchestration/board.html
ag-dashboard --registry ~/.claude/orchestration-repos.txt --serve --port 8787   # live
```

Charter view · items × steps grid (click a cell for its IN/OUT artifacts and check ratios) · open
threads. `waiting on human` is its own KPI so an approval backlog never reads as an engineering
backlog.

## Guarantees (the point of the system)

- **SDD** — nothing reaches agy without canonical `P/R/NG/AC` + `TP` + `IP`, gated by G1 and G2.
- **TDD** — Test Plan before code, **red state captured**, red→green verified, a passing test per `AC`.
- **DDD** — `glossary.md` is the ubiquitous language; `COMP` tags map spec → bounded context.
- **Role A/B separation** — every gate is an independent sub-agent with no authoring context.
- **Audit** — every step leaves an artifact with frontmatter, status, and a derived score; `RECORD`
  always closes with assumptions / discovered problems / possible bugs / open issues.
- **Trust boundary** — the git diff and the test run are the source of truth; agy's self-report never
  is. The Conductor owns the merge; agy never merges or pushes.

## Status

- **Contract:** complete (charter → epic → task, 3 human stops, 3 machine gates, collapse,
  escalation, rejection, autonomy dial, dispatch).
- **Migration:** templates, skills, and commands rewritten against it; the dashboard scanner and
  views rewritten and **verified against a fixture** (charter + full-form epic/story + collapsed
  bug) — scanner, static render, headless render of every view, and live `--serve` mode all pass.
- **Not yet run end-to-end on a real repo.** The previous 5-activity loop was validated
  `frame → close` on a pilot; this chain has not been.

## Known limitations

- **No migration path for records written under the old loop.** Existing `runs/<slug>/spec.md`
  directories are not read by the new scanner (it expects `prp`/`prd`/`story` + frontmatter). Old
  runs need re-homing or leaving behind.
- **`ag-init` resolves assets via a machine-local `$ORCH_HOME`** — not yet a portable plugin.
- **HG1 self-approval is the riskiest dial** — only the machine-generated-`SIG` condition is
  objectively checkable; the rest rely on the Conductor's honest self-report. Ships **off**.
- **Two checks are inherently non-mechanical** — `AC` testability and slice verticality. Judged by
  the gates, surfaced as findings, never faked with a regex.
- **v1 mints charter slices sequentially**, so a large charter's wall-clock is the sum of its slices.
  The `needs:` field is already in the schema, so parallel minting is a scheduler change.
- Verified against agy **v1.1.9**; CLI flags/JSON schema may drift — `agy-run.sh` extracts fields
  defensively.
