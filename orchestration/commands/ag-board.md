---
description: Render the orchestration board — charter view, items × steps grid with derived scores, and open threads. Static file or a live localhost server. Reads every artifact's frontmatter across charters/, epics/, and runs/.
argument-hint: "[repo ...] [--serve]   (default: registry, static file)"
---

Generate the cross-repo board and surface it. **One board covers all repos** — the data lives in
each repo's own `.orchestration/`; this pulls them together at render time.

1. Decide the scan source:
   - if `$ARGUMENTS` names repo paths, scan exactly those;
   - else scan the **registry** of every onboarded repo.
2. Run the generator (`ag-dashboard` on PATH, or `.orchestration/bin/ag-dashboard.py`):
   ```bash
   ag-dashboard --registry ~/.claude/orchestration-repos.txt \
     --out ~/.orchestration/board.html --title "Orchestration board"
   ```
   Or explicit repos / auto-discovery:
   ```bash
   ag-dashboard <repo> [<repo> ...] --out ~/.orchestration/board.html
   ag-dashboard --scan ~/WORK --out ~/.orchestration/board.html
   ```
3. **Live** (if the user asks for live, or passes `--serve`) — re-scans on every request, page
   auto-polls, binds to `127.0.0.1` only:
   ```bash
   ag-dashboard --registry ~/.claude/orchestration-repos.txt --serve --port 8787
   ```
   The server is long-running: start it in the background and give the user the URL — don't block
   the session waiting on it.
4. Report the item/charter/repo counts and the output path, then surface the file (open it in the
   browser preview, or send it). The HTML is self-contained — no server needed for the static form.

## What it shows

- **Charter view** — per charter: thesis, appetite burn, each `SL` with its state
  (`hypothesis` · `in-flight` · `done` · `cut`), the top-ranked `UNK`, and the next `review_after`.
  This is the level at which *"what is the state of the bet?"* is answerable without opening a
  child document.
- **Items × steps grid** — one row per item, one cell per step (`S1`…`S8` plus `G1/G2/G3` and the
  human gates `HG0/HG1/HG2`). Each cell carries a state and a **derived** score; clicking it shows
  that step's declared **IN** and **OUT** artifacts, its check ratios, and any findings attributed
  to it. Human gates are tinted differently, and `waiting on human` is its own KPI and filter — an
  approval backlog must never read as an engineering backlog.
- **Open threads** — every `ASM` and `OQ` still open, across every container, with the
  scope-blocking ones flagged first.

## Read it honestly

- **Every score is derived at scan time** from the artifact frontmatter and item graph per
  `templates/scoring.md`. Nothing on the board is a hand-written number; a score you disagree with
  is a disagreement with the checks, not with whoever closed the item.
- **`discovery_coverage` is shown as its own figure**, never folded into a score, because a pooled
  mean dilutes the most predictive number in the system out of visibility. Remember it counts an
  `assumed` aspect as covered — it measures *considered*, not *known*.
- **Two things are not mechanically checkable** and the board does not pretend otherwise: whether
  an `AC` is genuinely *testable*, and whether a charter slice is genuinely *vertical*. Both are
  judged by the G1/G2 assessors and reach the score only as findings.
- **Rejected items are shown but excluded from the score distributions.** Early rejection is a
  success, so scoring it would punish the workflow for working.
- A live `agy` delegation appears on its own (via each run's transient `running.json`, pid-liveness
  checked, so a crashed run never shows a false "running"); Claude sub-agents appear via the
  `.orchestration/agents/` breadcrumbs the `ag-init` hook writes.
