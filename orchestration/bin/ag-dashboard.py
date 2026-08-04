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

# ---------- artifact parsing: P/R/NG/AC/T/IM items + their up-links ----------
#
# The skills already author these as tagged markdown list items, e.g.
#   - **R1:** text… solves: P1 · part-of: FEAT1
#   - **AC1:** text… covers: R1 · in: COMP2
#   - **T1** [Happy] text… `covers: AC1`
#   - **IM1** text… `implements: AC1` `in: COMP1`
# so we parse that convention rather than asking anyone to re-author specs. The result is
# an item graph the board renders as linked chips (P → R → AC → T/IM).

# the colon may sit inside the bold (`**P1:**`, spec style) or after it (`**T1**`, TP style)
ITEM_RE = re.compile(r"^\s*[-*]\s+\*\*([A-Z]{1,4})(\d+):?\*\*:?\s*(.*)$")
LINK_RE = re.compile(
    r"\b(evidence|solves|covers|implements|part-of|in|deferred to|distilled from)\s*:\s*"
    r"([^·\n`]*)", re.I)
ID_RE = re.compile(r"\b([A-Z]{1,4}\d+)\b")
TRACE_KINDS = ("SIG", "ASK", "P", "R", "NG", "AC", "T", "IM")

def parse_items(text, only=None):
    """Parse tagged markdown list items into {id, kind, text, refs, tags}."""
    items, cur = [], None
    for line in (text or "").splitlines():
        m = ITEM_RE.match(line)
        if m:
            kind, n, rest = m.group(1).upper(), m.group(2), m.group(3)
            if only and kind not in only:
                cur = None
                continue
            cur = {"id": kind + n, "kind": kind, "raw": rest.strip()}
            items.append(cur)
        elif cur is not None:
            if line.strip() and (line.startswith(" ") or line.startswith("\t")):
                cur["raw"] += " " + line.strip()
            elif not line.strip():
                cur = None            # blank line ends the item
    for it in items:
        raw, refs, tags = it.pop("raw"), [], []
        for lm in LINK_RE.finditer(raw):
            key, val = lm.group(1).lower(), lm.group(2)
            for _id in ID_RE.findall(val):
                bucket = refs if re.match(r"^(SIG|ASK|P|R|NG|AC|T|IM)\d+$", _id) else tags
                if _id not in bucket:
                    bucket.append(_id)
        body = LINK_RE.sub("", raw)
        body = re.sub(r"`+", "", body)
        body = re.sub(r"\s*·\s*$", "", body).strip(" ·\t")
        # drop a trailing orphan link keyword left behind by the substitution
        body = re.sub(r"\b(evidence|solves|covers|implements|part-of|in|deferred to|"
                      r"distilled from)\s*:?\s*$", "", body, flags=re.I).strip(" ·,")
        it["text"], it["refs"], it["tags"] = body, refs, tags
    return items

def build_relations(items):
    """Trace map: id -> its ancestors ∪ descendants (its dependency chain).

    Directed on purpose. An undirected walk would leak sibling branches in through shared
    hubs (every P cites SIG1, so P1 would "relate" to every other problem's subtree).
    """
    known = {it["id"] for it in items}
    up = {it["id"]: [r for r in it["refs"] if r in known] for it in items}
    down = {}
    for src, targets in up.items():
        for t in targets:
            down.setdefault(t, []).append(src)

    def walk(start, edges):
        seen, stack = set(), list(edges.get(start, []))
        while stack:
            cur = stack.pop()
            if cur in seen or cur == start:
                continue
            seen.add(cur)
            stack.extend(edges.get(cur, []))
        return seen

    return {_id: sorted(walk(_id, up) | walk(_id, down)) for _id in known}

def framing_quality(items):
    """Score the FRAMING itself from its own structure: coverage + traceability.

    Each check is a ratio (share of items that pass), so the score degrades in proportion
    to how many items are broken — a low score always means more real gaps, not one flag.
    """
    by = lambda k: [i for i in items if i["kind"] == k]
    P, R, AC, T, IM, NG = (by(k) for k in ("P", "R", "AC", "T", "IM", "NG"))
    ids = lambda xs: {i["id"] for i in xs}
    refs_to = lambda xs, target_ids: {r for i in xs for r in i["refs"] if r in target_ids}

    checks = []
    def add(name, ok_n, total, detail, weight=1.0):
        if total <= 0:
            return
        checks.append({"name": name, "ratio": ok_n / total, "ok": ok_n, "total": total,
                       "detail": detail, "weight": weight})

    covered_P = refs_to(R, ids(P))
    add("Every problem has a requirement", len(covered_P), len(P),
        "problems with no requirement solving them")
    add("No orphan requirement", sum(1 for r in R if any(x in ids(P) for x in r["refs"])),
        len(R), "requirements that trace to no problem")
    covered_R = refs_to(AC, ids(R))
    add("Every requirement has an AC", len(covered_R), len(R),
        "requirements with no acceptance criterion")
    add("No orphan AC", sum(1 for a in AC if any(x in ids(R) for x in a["refs"])),
        len(AC), "ACs that cover no requirement")
    if T:
        tested = refs_to(T, ids(AC))
        add("Every AC has a test", len(tested), len(AC), "ACs with no test in the TP", 1.2)
    if IM:
        built = refs_to(IM, ids(AC))
        add("Every AC has an impl step", len(built), len(AC), "ACs with no step in the IP")
    if P or R:
        add("Scope bounded (non-goals stated)", 1 if NG else 0, 1,
            "no non-goals recorded — scope is unbounded", 0.5)

    if not checks:
        return None
    wsum = sum(c["weight"] for c in checks)
    score = round(100 * sum(c["ratio"] * c["weight"] for c in checks) / wsum)
    return {"score": score, "checks": checks,
            "counts": {"P": len(P), "R": len(R), "AC": len(AC),
                       "NG": len(NG), "T": len(T), "IM": len(IM)}}

def scan_artifacts(run_dir):
    """Parse spec.md + TP.md + IP.md into one linked item graph for this run."""
    items = []
    spec = os.path.join(run_dir, "spec.md")
    if os.path.exists(spec):
        items += parse_items(_read_text(spec, 40000),
                             only=("SIG", "ASK", "P", "R", "NG", "AC"))
    tp = os.path.join(run_dir, "TP.md")
    if os.path.exists(tp):
        items += parse_items(_read_text(tp, 30000), only=("T",))
    ip = os.path.join(run_dir, "IP.md")
    if os.path.exists(ip):
        items += parse_items(_read_text(ip, 30000), only=("IM",))
    if not items:
        return None
    seen, uniq = set(), []
    for it in items:                      # ids are unique per kind; keep first wins
        if it["id"] in seen:
            continue
        seen.add(it["id"]); uniq.append(it)
    return {"items": uniq, "rel": build_relations(uniq), "framing": framing_quality(uniq)}

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

# ---------- output quality: sub-scores that roll up to the overall ----------
#
# Content quality, not process throughput: every dimension is driven by countable evidence
# from the closing record, so "more problems recorded" always means "lower score". A run
# may override any dimension by writing `metrics.quality: { tests: 80, … }` in RECORD.md.

QUALITY_DIMS = [
    ("acceptance", "Acceptance", 0.30),
    ("tests",      "Tests",      0.25),
    ("defects",    "Defects",    0.20),
    ("security",   "Security",   0.10),
    ("risk",       "Assumptions & risk", 0.08),
    ("followups",  "Open follow-ups",    0.07),
]

def _clamp(v):
    return max(0, min(100, int(round(v))))

def output_quality(rec, framing=None):
    """Per-dimension output scores + the rolled-up overall. Returns None pre-review."""
    m = rec.get("metrics") or {}
    rv = m.get("review") or {}
    dl = m.get("delegate") or {}
    cl = rec.get("closing") or {}
    override = m.get("quality") if isinstance(m.get("quality"), dict) else {}

    n_bugs = len(cl.get("bugs") or [])
    n_assume = len(cl.get("assumptions") or [])
    n_issues = len(cl.get("issues") or [])
    n_probs = len(cl.get("problems") or [])
    sec = num_or(rv.get("security_findings"), 0)
    good = num_or(rv.get("ac_good"), 0)
    flagged = num_or(rv.get("ac_flagged"), 0)
    overdue = num_or(rv.get("ac_overdue"), 0)
    graded = good + flagged + overdue

    dims, why = {}, {}
    # Acceptance — how many ACs actually landed good
    if graded:
        dims["acceptance"] = _clamp(100 * (good + 0.5 * flagged) / graded)
        why["acceptance"] = "%d good · %d flagged · %d failed" % (good, flagged, overdue)
    elif rec.get("tests") in ("pass", "fail"):
        dims["acceptance"] = 100 if rec["tests"] == "pass" else 0
        why["acceptance"] = "no per-AC grading; tests %s" % rec["tests"]
    # Tests — did they pass, and was red→green actually proven
    t = rec.get("tests")
    if t in ("pass", "fail"):
        base = 100 if t == "pass" else 0
        if t == "pass" and (m.get("plan") or {}).get("red_captured") is False:
            base -= 25                      # green with no proven red = weak evidence
            why["tests"] = "pass, but no red state captured"
        else:
            why["tests"] = "tests %s" % t
        dims["tests"] = _clamp(base)
    # Defects — each recorded possible bug is a real deduction
    dims["defects"] = _clamp(100 - 25 * n_bugs)
    why["defects"] = "%d possible bug(s)" % n_bugs
    # Security — unresolved findings bite hard
    dims["security"] = _clamp(100 - 34 * sec)
    why["security"] = "%d finding(s)" % sec
    # Assumptions & discovered problems = carried risk
    dims["risk"] = _clamp(100 - 12 * n_assume - 8 * n_probs)
    why["risk"] = "%d assumption(s) · %d discovered problem(s)" % (n_assume, n_probs)
    # Debt left behind
    dims["followups"] = _clamp(100 - 15 * n_issues)
    why["followups"] = "%d open issue(s)" % n_issues

    for k, v in override.items():
        if isinstance(v, (int, float)):
            dims[k] = _clamp(v)
            why[k] = "set in RECORD"

    present = [(k, lbl, w) for k, lbl, w in QUALITY_DIMS if k in dims]
    if not present:
        return None
    wsum = sum(w for _, _, w in present)
    overall = _clamp(sum(dims[k] * w for k, _, w in present) / wsum)

    caps = []
    if rec.get("status") == "blocked":
        caps.append("blocked")
    if rec.get("tests") == "fail":
        caps.append("tests failing")
    if caps:
        overall = min(overall, 40)

    return {"overall": overall,
            "dims": [{"key": k, "label": lbl, "weight": w,
                      "score": dims[k], "why": why.get(k, "")} for k, lbl, w in present],
            "caps": caps,
            "counts": {"bugs": n_bugs, "assumptions": n_assume, "issues": n_issues,
                       "problems": n_probs, "security": sec,
                       "iterations": num_or(dl.get("iterations"), None)}}

def num_or(v, default):
    return v if isinstance(v, (int, float)) else default

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
    q = rec.get("quality") or {}
    score = q.get("overall", (rec.get("metrics") or {}).get("overall_score"))
    if isinstance(score, (int, float)) and score < 60:
        weakest = min(q.get("dims") or [], key=lambda d: d["score"], default=None)
        return "low score (%s)%s" % (score, " — weakest: " + weakest["label"] if weakest else "")
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
        # framing (left panel): the parsed P/R/NG/AC/T/IM item graph + its quality
        arts = scan_artifacts(run_dir)
        if arts:
            rec["artifacts"] = arts
            if arts.get("framing"):
                rec["framingScore"] = arts["framing"]["score"]

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
        rec["quality"] = output_quality(rec)
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
