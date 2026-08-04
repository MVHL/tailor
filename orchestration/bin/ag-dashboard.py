#!/usr/bin/env python3
"""
ag-dashboard.py — scan one or more repos' .orchestration/runs and render a single
self-contained HTML triage board.

The board is overview-first: it surfaces what needs attention (blocked, awaiting a
decision, in review, failing, or low-scoring), then lets you drill into any run. It reads
the RECORD.md frontmatter (+ closing sections) that `ag-close` writes, and also picks up
in-flight runs that have no RECORD yet by inferring their stage from which files exist.

Usage:
  ag-dashboard.py [REPO ...] [--registry FILE] [--scan ROOT] [--out FILE] [--title TITLE]

  REPO         one or more repo roots to scan. A repo is included if it contains
               .orchestration/runs/. Non-orchestrated paths are skipped.
  --registry   file of repo paths (one per line, # comments ok). ag-init appends each
               onboarded repo to ~/.claude/orchestration-repos.txt — pass that here to get
               one board across every repo you've onboarded.
  --scan ROOT  auto-discover: walk ROOT (depth ≤ 4) for any repo containing
               .orchestration/runs/. Repeatable. Use instead of a registry.
  --out        output HTML path (default: ./ag-dashboard.html)
  --title      board title (default: "Orchestration board")

  Sources combine (REPO + registry + scan) and are de-duplicated by absolute path. With no
  source at all, defaults to the current directory.

No third-party dependencies (frontmatter is parsed with a small tolerant parser for the
known RECORD schema). Open the output file directly, or serve the folder.
"""
import sys, os, json, glob, re, time, html as _html

# A "running" sub-agent breadcrumb older than this with no close event is presumed
# orphaned (hard-killed session, crashed hook, etc.) rather than genuinely still live.
STALE_AFTER_SECONDS = 30 * 60

def _json_for_script(payload):
    """json.dumps, but safe to inline inside a <script> block.

    json.dumps does not escape "</" — if any field in payload (a RECORD.md title,
    a closing-section bullet, an agy result snippet, ...) contains the literal
    substring "</script>", a naive inline dump closes the script tag early and the
    rest is parsed as HTML, corrupting or blanking the page. Escaping the forward
    slash after "<" is the standard fix (valid inside a JS string; browsers don't
    require "/" to be escaped, so this changes nothing else about the JSON).
    """
    return json.dumps(payload).replace("</", "<\\/")

def _escape_title(title):
    """HTML-escape a --title value before inlining into <title>/<h1> text nodes."""
    return _html.escape(title, quote=True)

_HERE = os.path.dirname(os.path.realpath(__file__))  # realpath: resolve the PATH symlink
# Template lives in ../templates when run from source, or next to the script when
# ag-init copies both into a repo's .orchestration/bin/.
TEMPLATE = next((p for p in (
    os.path.join(_HERE, "..", "templates", "dashboard.html"),
    os.path.join(_HERE, "dashboard.html"),
) if os.path.exists(p)), os.path.join(_HERE, "..", "templates", "dashboard.html"))

# ---------- tiny frontmatter parser (known RECORD schema; no yaml dep) ----------

def _coerce(v):
    v = v.strip()
    if v == "" or v == '""' or v == "''":
        return ""
    if (v[0], v[-1]) in (('"', '"'), ("'", "'")):
        return v[1:-1]
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v

def _parse_list(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_coerce(x) for x in inner.split(",")]
    return _coerce(v)

def _parse_inline_dict(v):
    # "{ score: 100, red_captured: true }"
    v = v.strip()
    if v.startswith("{"):
        v = v[1:]
    if v.endswith("}"):
        v = v[:-1]
    out = {}
    for part in v.split(","):
        if ":" not in part:
            continue
        k, val = part.split(":", 1)
        out[k.strip()] = _coerce(val)
    return out

def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = text[3:end].strip("\n")
    body = text[end + 4:]
    data, in_metrics = {}, False
    metrics = {}
    for line in fm.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^\S", line):            # top-level key
            in_metrics = False
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if key == "metrics":
                in_metrics = True
                continue
            if val.startswith("["):
                data[key] = _parse_list(val)
            else:
                data[key] = _coerce(val)
        elif in_metrics:                      # indented under metrics:
            key, _, val = line.strip().partition(":")
            key, val = key.strip(), val.strip()
            if val.startswith("{"):
                metrics[key] = _parse_inline_dict(val)
            else:
                metrics[key] = _coerce(val)
    if metrics:
        data["metrics"] = metrics
    return data, body

# ---------- closing-section extraction ----------

SECTIONS = {"assumptions": "Assumptions", "problems": "Discovered problems",
            "bugs": "Possible bugs", "issues": "Open issues"}

def extract_closing(body):
    out = {k: [] for k in SECTIONS}
    what = ""
    m = re.search(r"##\s*What shipped\s*\n(.+?)(\n##|\Z)", body, re.S)
    if m:
        what = " ".join(m.group(1).split())
    for key, heading in SECTIONS.items():
        m = re.search(r"##\s*" + re.escape(heading) + r"\s*\n(.*?)(\n##|\Z)", body, re.S)
        if not m:
            continue
        for ln in m.group(1).splitlines():
            ln = ln.strip()
            if ln.startswith("- "):
                item = ln[2:].strip()
                if item and item.lower() != "none.":
                    out[key].append(item)
    return what, out

# ---------- stage inference for in-flight runs (no RECORD yet) ----------

def infer_stage(run_dir):
    has = lambda p: os.path.exists(os.path.join(run_dir, p))
    result = bool(glob.glob(os.path.join(run_dir, "result.iter*.json")))
    if has("TP.md") and has("IP.md"):
        planned = True
    else:
        planned = False
    if result:
        return "delegated"
    if planned:
        return "planned"
    if has("spec.md"):
        return "framed"
    return "started"

# ---------- live markers (Gap A: agy running; Gap B: Claude sub-agents) ----------

def is_alive(pid):
    """True if a local process with this pid exists (same-host board only)."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)          # signal 0 = existence/permission probe, no-op
    except ProcessLookupError:
        return False
    except PermissionError:
        return True              # exists, owned by someone else
    except OSError:
        return False
    return True

def scan_running(run_dir):
    """Read a run's transient running.json (agy delegating NOW), or None."""
    path = os.path.join(run_dir, "running.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            mark = json.load(fh)
    except (ValueError, OSError):
        return None
    mark["alive"] = is_alive(mark.get("pid"))
    mark["marker"] = "running.json"
    return mark

def _seconds_since(iso_ts):
    """Best-effort age in seconds for an ISO-8601 UTC 'started' timestamp."""
    if not iso_ts:
        return None
    try:
        import calendar
        t = time.strptime(iso_ts, "%Y-%m-%dT%H:%M:%SZ")
        return time.time() - calendar.timegm(t)
    except ValueError:
        return None

def scan_agents(repo):
    """Read committed Claude sub-agent breadcrumbs from .orchestration/agents/.

    A breadcrumb is only closed by a matching PostToolUse hook firing (see
    ag-agent-hook.py). A hard-killed session, crashed hook, or SIGKILL'd sub-agent
    never fires that event, so `status` can be stuck at "running" forever with no
    self-healing path (CLAUDE.md documents this as a known gap). Rather than trust
    a stale "running" status at face value indefinitely, treat one older than
    STALE_AFTER_SECONDS as presumed-orphaned: don't render it as live, and surface
    it distinctly ("stale") so it doesn't read as an active, in-progress agent.
    """
    repo = os.path.abspath(repo)
    adir = os.path.join(repo, ".orchestration", "agents")
    repo_name = os.path.basename(repo.rstrip("/"))
    out = []
    for f in sorted(glob.glob(os.path.join(adir, "*.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                rec = json.load(fh)
        except (ValueError, OSError):
            continue
        rec["repo"] = repo_name
        rec["repoPath"] = repo
        rec["path"] = f
        running = rec.get("status") == "running"
        age = _seconds_since(rec.get("started")) if running else None
        stale = bool(running and age is not None and age > STALE_AFTER_SECONDS)
        if stale:
            rec["status"] = "stale"
        rec["live"] = running and not stale
        out.append(rec)
    # newest first by start time
    out.sort(key=lambda r: r.get("started", ""), reverse=True)
    return out

def _read_text(path, limit=12000):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            t = fh.read(limit + 1)
    except OSError:
        return ""
    return (t[:limit] + "\n…(truncated)") if len(t) > limit else t

def scan_delegations(run_dir):
    """Read a run's delegations.jsonl (one agy sub-session per line), oldest→newest."""
    path = os.path.join(run_dir, "delegations.jsonl")
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out

# ---------- session tree: normalise agy delegations + Claude sub-agents to child nodes ----

def agy_child(d, live=False):
    return {"kind": "agy", "who": "agy",
            "label": "agy delegation · iter %s" % d.get("iteration", "?"),
            "model": d.get("model", ""), "effort": d.get("effort", ""),
            "status": ("running" if live else d.get("status", "done")),
            "live": bool(live), "result": d.get("result", ""),
            "iteration": d.get("iteration"), "tokens": None,
            "started": d.get("started", ""), "finished": d.get("finished", "")}

def sub_child(a):
    return {"kind": "claude-subagent", "who": a.get("agent_type", "sub-agent"),
            "label": a.get("purpose", ""), "model": a.get("model") or "claude",
            "status": a.get("status", "?"), "live": a.get("status") == "running",
            "result": "", "tokens": a.get("tokens"),
            "started": a.get("started", ""), "finished": a.get("finished", ""),
            "id": a.get("id", "")}

# ---------- attention logic ----------

def attention(rec):
    run = rec.get("running")
    if run and run.get("alive"):
        it = run.get("iteration")
        return f"agy delegating now (iter {it})" if it else "agy delegating now"
    status = rec.get("status", "")
    if status in ("blocked", "awaiting-decision"):
        return f"status: {status}"
    if status == "in-review":
        return "awaiting review sign-off"
    if rec.get("tests") == "fail":
        return "tests failing"
    m = rec.get("metrics") or {}
    score = m.get("overall_score")
    if isinstance(score, (int, float)) and score < 60:
        return f"low score ({score})"
    if rec.get("closing", {}).get("bugs"):
        return "possible bugs recorded"
    if status == "in-progress":
        return f"in progress ({rec.get('stage','')})"
    return ""

# ---------- scan ----------

def scan_repo(repo):
    repo = os.path.abspath(repo)
    runs_dir = os.path.join(repo, ".orchestration", "runs")
    if not os.path.isdir(runs_dir):
        return []
    repo_name = os.path.basename(repo.rstrip("/"))
    out = []
    for run_dir in sorted(glob.glob(os.path.join(runs_dir, "*"))):
        if not os.path.isdir(run_dir):
            continue
        task_id = os.path.basename(run_dir)
        record = os.path.join(run_dir, "RECORD.md")
        rec = {"repo": repo_name, "repoPath": repo, "task": task_id,
               "runPath": run_dir, "closing": {k: [] for k in SECTIONS}}
        if os.path.exists(record):
            with open(record, encoding="utf-8", errors="replace") as fh:
                data, body = parse_frontmatter(fh.read())
            rec.update(data)
            what, closing = extract_closing(body)
            rec["whatShipped"], rec["closing"] = what, closing
            rec["recordPath"] = record
            rec.setdefault("stage", "closed")
        else:
            rec["status"] = "in-progress"
            rec["stage"] = infer_stage(run_dir)
            # title fallback from spec.md first heading
            spec = os.path.join(run_dir, "spec.md")
            if os.path.exists(spec):
                with open(spec, encoding="utf-8", errors="replace") as fh:
                    first = fh.readline().strip("# \n")
                rec["title"] = first or task_id
        # framing (left panel input): the spec P/R/NG/AC, plus brief if present
        spec_path = os.path.join(run_dir, "spec.md")
        if os.path.exists(spec_path):
            rec["spec"] = _read_text(spec_path)
        brief_path = os.path.join(run_dir, "brief.md")
        if os.path.exists(brief_path):
            rec["brief"] = _read_text(brief_path, 8000)

        # agy delegations become child sub-sessions; newest running.json (if alive) too
        delegs = scan_delegations(run_dir)
        agy_children = []
        for d in delegs:
            c = agy_child(d)
            rp = os.path.join(run_dir, "result.iter%s.txt" % (d.get("iteration") or ""))
            if os.path.exists(rp):
                c["result_full"] = _read_text(rp, 6000)
            agy_children.append(c)
        run = scan_running(run_dir)
        if run:
            rec["running"] = run
            if run.get("alive"):
                rec["live"] = True
                rec["stage"] = "delegating (iter %s)" % run.get("iteration", "?")
                agy_children.append(agy_child({"iteration": run.get("iteration"),
                    "model": run.get("model", ""), "effort": run.get("effort", ""),
                    "started": run.get("started", "")}, live=True))
        rec["agyChildren"] = agy_children
        # task-level model = the agy model that ran (a live delegation wins, else the last)
        if run and run.get("alive"):
            rec["model"] = run.get("model", "")
        elif delegs:
            rec["model"] = delegs[-1].get("model", "")
        else:
            rec["model"] = ""
        rec["title"] = rec.get("title") or task_id
        rec["attention"] = attention(rec)
        rec["needsAttention"] = bool(rec["attention"])
        out.append(rec)
    return out

def read_registry(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.split("#", 1)[0].strip()
            if ln:
                out.append(os.path.expanduser(ln))
    return out

def discover(root, max_depth=4):
    root = os.path.abspath(os.path.expanduser(root))
    found = []
    base = root.rstrip("/").count("/")
    for dirpath, dirnames, _ in os.walk(root):
        depth = dirpath.count("/") - base
        if depth > max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "worktrees")]
        if os.path.isdir(os.path.join(dirpath, ".orchestration", "runs")):
            found.append(dirpath)
            dirnames[:] = []   # don't descend into an orchestrated repo
    return found

def build_payload(repos, title):
    """Scan every repo NOW and return the board payload (used per-request in serve mode).

    Each run carries a `children` list — its sub-sessions: agy delegations first, then the
    Claude sub-agents that ran under it. Sub-agents whose task doesn't map to a known run
    are grouped under a synthetic "(unassigned)" parent per repo, so the tree is complete.
    """
    runs, agents = [], []
    for r in repos:
        runs.extend(scan_repo(r))
        agents.extend(scan_agents(r))
    agents.sort(key=lambda a: a.get("started", ""), reverse=True)

    by_key = {(r["repo"], r["task"]): r for r in runs}
    orphans = {}
    for a in agents:
        run = by_key.get((a.get("repo"), a.get("task")))
        if run is None:
            orphans.setdefault(a.get("repo"), []).append(a)
        else:
            run.setdefault("_subs", []).append(a)

    for r in runs:
        subs = sorted(r.pop("_subs", []), key=lambda a: a.get("started", ""), reverse=True)
        r["children"] = (r.pop("agyChildren", []) or []) + [sub_child(a) for a in subs]
        r["live"] = bool(r.get("live")) or any(c["live"] for c in r["children"])
        if not r.get("needsAttention"):
            bad = next((c for c in r["children"] if c["status"] in ("failed", "timeout")), None)
            if bad:
                r["attention"] = "%s %s" % (bad["who"], bad["status"])
                r["needsAttention"] = True

    for repo, subs in orphans.items():
        subs = sorted(subs, key=lambda a: a.get("started", ""), reverse=True)
        children = [sub_child(a) for a in subs]
        runs.append({"repo": repo, "repoPath": subs[0].get("repoPath", ""),
                     "task": "(unassigned)", "title": "Unassigned sub-agents",
                     "status": "in-progress", "stage": "", "synthetic": True,
                     "model": "", "children": children,
                     "live": any(c["live"] for c in children),
                     "closing": {k: [] for k in SECTIONS}, "metrics": {},
                     "attention": "", "needsAttention": False})

    return {"title": title, "runs": runs, "agents": agents, "repos": list(repos)}

def dedup_repos(repos):
    seen, uniq = set(), []
    for r in repos:
        ap = os.path.abspath(os.path.expanduser(r))
        if ap not in seen:
            seen.add(ap); uniq.append(ap)
    return uniq

def render_static(repos, title, out_file):
    payload = build_payload(repos, title)
    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()
    html = html.replace("/*__AG_DATA__*/null", _json_for_script(payload))
    html = html.replace("__AG_TITLE__", _escape_title(title))
    with open(out_file, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote {out_file} — {len(payload['runs'])} run(s) from {len(repos)} repo(s)")

def serve(repos, title, port):
    """Local read-only live server. Binds to 127.0.0.1 only. Re-scans on each /api/runs."""
    import http.server, socketserver
    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read().replace("/*__AG_LIVE__*/false", "true").replace("__AG_TITLE__", _escape_title(title))
    page_bytes = page.encode("utf-8")

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):  # quiet
            pass
        def _send(self, body, ctype):
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/api/runs":
                # served as its own JSON response (not inlined into <script>), so plain
                # json.dumps is fine here — no "</script>" html-parser risk over this path.
                body = json.dumps(build_payload(repos, title)).encode("utf-8")
                self._send(body, "application/json; charset=utf-8")
            elif path in ("/", "/index.html"):
                self._send(page_bytes, "text/html; charset=utf-8")
            else:
                self.send_response(404); self.end_headers()

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with Server(("127.0.0.1", port), Handler) as httpd:
        url = f"http://127.0.0.1:{port}"
        print(f"live board on {url}  (re-scans {len(repos)} repo(s) on each request; Ctrl-C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")

def main(argv):
    repos, out_file, title = [], "ag-dashboard.html", "Orchestration board"
    do_serve, port = False, 8787
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--out":
            out_file = argv[i + 1]; i += 2
        elif a == "--title":
            title = argv[i + 1]; i += 2
        elif a == "--registry":
            repos.extend(read_registry(argv[i + 1])); i += 2
        elif a == "--scan":
            repos.extend(discover(argv[i + 1])); i += 2
        elif a == "--serve":
            do_serve = True; i += 1
        elif a == "--port":
            port = int(argv[i + 1]); i += 2
        else:
            repos.append(a); i += 1
    if not repos:
        repos = ["."]
    repos = dedup_repos(repos)
    if do_serve:
        serve(repos, title, port)
    else:
        render_static(repos, title, out_file)

if __name__ == "__main__":
    main(sys.argv[1:])
