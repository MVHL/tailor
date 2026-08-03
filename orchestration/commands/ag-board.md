---
description: Render the orchestration triage dashboard — overview of every task across repos (needs-attention first), then drill in. Static file, or a live localhost server. Reads .orchestration/runs/*/RECORD.md.
argument-hint: "[repo ...] [--serve]   (default: registry, static file)"
---

Generate the cross-repo triage board and open it. **One board covers all repos** — the data
lives in each repo's own `.orchestration/runs/`; this pulls them together at render time.

**Live vs static.** By default this writes a static HTML snapshot (re-run to refresh). If the
user asks for a *live* board (or passes `--serve`), start the local server instead — it
re-scans on every request and the page auto-polls, so it stays current without regenerating:
```bash
# live: localhost server, auto-refreshing (Ctrl-C to stop). Binds to 127.0.0.1 only.
ag-dashboard --registry ~/.claude/orchestration-repos.txt --serve --port 8787
# then open http://127.0.0.1:8787
```
The server is long-running — start it in the background (or tell the user to run it in their
own terminal) and give them the URL; don't block the session waiting on it.

1. Decide the scan source:
   - if `$ARGUMENTS` names repo paths, scan exactly those → write to `~/.orchestration/board.html`;
   - else (no args) scan the **registry** of every onboarded repo → the default cross-repo board.
2. Run the generator (`ag-dashboard` on PATH, or `.orchestration/bin/ag-dashboard.py`):
   ```bash
   # default: all onboarded repos, one board
   ag-dashboard --registry ~/.claude/orchestration-repos.txt \
     --out ~/.orchestration/board.html --title "Orchestration board"
   # or explicit repos
   ag-dashboard <repo> [<repo> ...] --out ~/.orchestration/board.html
   # or auto-discover under a root instead of a registry
   ag-dashboard --scan ~/WORK --out ~/.orchestration/board.html
   ```
   It parses each run's `RECORD.md` frontmatter + closing sections, de-duplicates repos, and
   picks up in-flight runs (no RECORD yet) by inferring their stage from which files exist.
3. Report the run/repo counts and the output path, then surface the file to the user (open it
   in the browser preview, or send it). The HTML is self-contained — no server needed.

The board is overview-first: KPI row (tasks, needs-attention, first-pass rate, avg score,
agy tokens/time), a **Needs attention** section (blocked / awaiting-decision / in-review /
failing / low-score, sorted by severity), analytics (avg score per step, score
distribution), and a sortable/filterable table where each row drills into the run's metrics
and closing record.
