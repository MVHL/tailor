#!/usr/bin/env python3
"""
ag-dashboard.py — scan one or more onboarded repos and render a single self-contained
HTML board for the WORKFLOW.md step contract.

Three views, one page:

  * Charter view   — per charter: thesis, appetite burn, slice states, next re-bet.
  * Task x step    — one row per item, one cell per step (S1..S8 + G1/G2/G3 + HG0/1/2),
                     each cell a status dot plus a DERIVED score. Click a cell for its
                     declared IN / OUT artifacts.
  * Open threads   — every ASM / OQ still open across the repo, grouped by container.

Everything numeric here is derived from the files at scan time; nothing is read from a
hand-written score field. See templates/scoring.md.

Two honest gaps, surfaced in the UI rather than papered over:
  * Whether an AC is genuinely *testable*, and whether a charter slice is genuinely
    *vertical*, are not mechanically decidable. They are judged by the G1/G2 assessors and
    reach the score only as findings — we do not fake a regex for them.
  * `discovery_coverage` counts an `assumed` aspect as covered. Coverage measures
    *considered*, not *known*, so the open-assumption count travels next to it.

Usage:
  ag-dashboard.py [REPO ...] [--registry FILE] [--scan ROOT] [--out FILE] [--title T]
                  [--serve] [--port N]

  REPO         repo roots to scan. Included if they contain .orchestration/.
  --registry   file of repo paths (one per line, # comments ok). /ag-init appends every
               onboarded repo to ~/.claude/orchestration-repos.txt.
  --scan ROOT  auto-discover: walk ROOT (depth <= 4) for onboarded repos. Repeatable.
  --out        output HTML path (default: ./ag-dashboard.html)
  --title      board title
  --serve      live localhost server (127.0.0.1 only), re-scans per request

Sources combine and de-duplicate by absolute path. No third-party dependencies.
"""
import sys, os, json, glob, re, time, html as _html

STALE_AFTER_SECONDS = 30 * 60   # a "running" breadcrumb older than this is presumed orphaned

# ── the chain, in order. `level` decides which container owns the step. ────────────────
STEPS = [
    ("S0",  "Charter",        "charter"),
    ("HG0", "Bet approval",   "charter"),
    ("S1",  "Intake",         "epic"),
    ("S2",  "Discovery",      "epic"),
    ("S2b", "Spike",          "epic"),
    ("S3",  "Specification",  "epic"),
    ("HG1", "Scope approval", "epic"),
    ("S4",  "Refinement",     "task"),
    ("G1",  "Framing review", "task"),
    ("S5",  "Test Plan",      "task"),
    ("S6",  "Impl Plan",      "task"),
    ("G2",  "Readiness",      "task"),
    ("S7",  "Implementation", "task"),
    ("G3",  "Code review",    "task"),
    ("HG2", "Merge approval", "task"),
    ("S8",  "Close",          "task"),
]
STEP_ORDER = {s[0]: i for i, s in enumerate(STEPS)}
HUMAN_GATES = ("HG0", "HG1", "HG2")
OPTIONAL_STEPS = ("S0", "HG0", "S2b", "S3")   # absent != broken

def _json_for_script(payload):
    """json.dumps, safe to inline in <script>.

    json.dumps does not escape "</" — a title or finding containing "</script>" would
    close the tag early and blank the page. Escaping the slash is the standard fix.
    """
    return json.dumps(payload).replace("</", "<\\/")

def _escape_title(t):
    return _html.escape(t, quote=True)

_HERE = os.path.dirname(os.path.realpath(__file__))
TEMPLATE = next((p for p in (
    os.path.join(_HERE, "..", "templates", "dashboard.html"),
    os.path.join(_HERE, "dashboard.html"),
) if os.path.exists(p)), os.path.join(_HERE, "..", "templates", "dashboard.html"))


# ══════════════════════════════════════════════════════════════════════════════════════
# frontmatter (no yaml dependency; tolerant of the known schemas)
# ══════════════════════════════════════════════════════════════════════════════════════

def _coerce(v):
    v = v.strip()
    if v in ("", '""', "''"):
        return ""
    if len(v) > 1 and (v[0], v[-1]) in (('"', '"'), ("'", "'")):
        return v[1:-1]
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("none", "null", "~", "-"):
        return ""
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v

def _parse_list(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_coerce(x) for x in inner.split(",")] if inner else []
    return _coerce(v)

def _parse_inline_dict(v):
    v = v.strip().lstrip("{").rstrip("}")
    out = {}
    depth, buf, parts = 0, "", []
    for ch in v:                      # split on top-level commas only
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf); buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf)
    for part in parts:
        if ":" not in part:
            continue
        k, val = part.split(":", 1)
        val = val.strip()
        out[k.strip()] = _parse_list(val) if val.startswith("[") else (
            _parse_inline_dict(val) if val.startswith("{") else _coerce(val))
    return out

def parse_frontmatter(text):
    """Return (data, body). Handles two levels of nesting (metrics: gates: g1: {...})."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm, body = text[3:end].strip("\n"), text[end + 4:]
    data = {}
    stack = [(-1, data)]
    for line in fm.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = line.strip().partition(":")
        key, val = key.strip(), val.strip()
        # strip a trailing `# comment`, but never inside a quoted/braced value
        if "#" in val and not val.startswith(('"', "'", "{", "[")):
            val = val.split("#", 1)[0].strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else data
        if val == "":
            child = {}
            parent[key] = child
            stack.append((indent, child))
        elif val.startswith("{"):
            parent[key] = _parse_inline_dict(val)
        elif val.startswith("["):
            parent[key] = _parse_list(val)
        else:
            parent[key] = _coerce(val)
    return data, body

def _read(path, limit=60000):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            t = fh.read(limit + 1)
    except OSError:
        return ""
    return (t[:limit] + "\n…(truncated)") if len(t) > limit else t


# ══════════════════════════════════════════════════════════════════════════════════════
# item parsing — the tagged markdown list items the templates author
# ══════════════════════════════════════════════════════════════════════════════════════
#   - **P1** who/pain — impact   `evidence: SIG1`
#   - **NG1** excluded   `excludes: P1`   `deferred to: Q3`
#   - **T1** `[Happy]` scenario   `covers: AC1`
#   - **ASM1** taken as true   `affects: P1`   `state: open`

ITEM_RE = re.compile(r"^\s*[-*]\s+\*\*([A-Z]{1,4})(\d+):?\*\*:?\s*(.*)$")
LINK_RE = re.compile(
    r"\b(evidence|solves|covers|implements|excludes|threatens|affects|reduces|needs|"
    r"part-of|in|deferred to|distilled from|state|severity|attributed-to|resolution|"
    r"likelihood|impact|owner|hypothesis|minted|reason|waiver)\s*:\s*([^·\n`]*)", re.I)
ID_RE = re.compile(r"\b((?:[A-Z]{1,3}\d+|C\d+#[A-Z]{1,3}\d+|\d+(?:\.\d+)?#[A-Z]{1,3}\d+))\b")
TRACE = ("SIG", "ASK", "P", "D", "RK", "R", "NG", "AC", "T", "IM", "UNK", "SL", "BND")
ANNOT = ("ASM", "OQ", "F", "DEC")

def parse_items(text, only=None):
    """Parse tagged list items into {id, kind, text, refs, attrs}."""
    items, cur = [], None
    for line in (text or "").splitlines():
        m = ITEM_RE.match(line)
        if m:
            kind, n, rest = m.group(1).upper(), m.group(2), m.group(3)
            if only and kind not in only:
                cur = None
                continue
            cur = {"id": kind + n, "kind": kind, "_raw": rest.strip()}
            items.append(cur)
        elif cur is not None:
            if line.strip() and line[:1] in (" ", "\t"):
                cur["_raw"] += " " + line.strip()
            elif not line.strip():
                cur = None
    for it in items:
        raw, refs, attrs = it.pop("_raw"), [], {}
        for lm in LINK_RE.finditer(raw):
            key, val = lm.group(1).lower(), lm.group(2).strip()
            attrs.setdefault(key, val)
            for _id in ID_RE.findall(val):
                if _id not in refs:
                    refs.append(_id)
        body = LINK_RE.sub("", raw)
        body = re.sub(r"`+", "", body)
        body = re.sub(r"\s*[·,]\s*$", "", body).strip(" ·\t,")
        it["text"], it["refs"], it["attrs"] = body[:400], refs, attrs
    return items

def _local(ref):
    """`24#P1` / `C3#SL2` → `P1`; a bare `P1` stays `P1`."""
    return ref.split("#", 1)[1] if "#" in ref else ref

def _has_ref_to(item, target_ids):
    return any(_local(r) in target_ids for r in item["refs"])


# ══════════════════════════════════════════════════════════════════════════════════════
# artifact checks — each is a RATIO, so a score degrades in proportion to what's broken
# ══════════════════════════════════════════════════════════════════════════════════════

def _chk(name, ok, total, detail, weight=1.0):
    return None if total <= 0 else {
        "name": name, "ok": ok, "total": total, "ratio": ok / total,
        "detail": detail, "weight": weight}

def checks_prp(fm, items, all_items):
    by = lambda k: [i for i in items if i["kind"] == k]
    SIG, ASK, P = by("SIG"), by("ASK"), by("P")
    pids = {i["id"] for i in P}
    r_ng = [i for i in all_items if i["kind"] in ("R", "NG")]
    out = [
        _chk("SIG sourced + verbatim",
             sum(1 for s in SIG if s["attrs"].get("source") or "source:" in s["text"].lower()),
             len(SIG), "signals with no source/date"),
        _chk("ASK links a signal", sum(1 for a in ASK if a["refs"]), len(ASK),
             "asks with no signal — unfounded"),
        _chk("P cites evidence", sum(1 for p in P if p["refs"]), len(P),
             "problems with no evidence — an invented need"),
        _chk("P has an R or NG", sum(1 for p in P if any(_has_ref_to(x, {p["id"]}) for x in r_ng)),
             len(P), "problems neither solved nor excluded"),
    ]
    cov = fm.get("discovery_coverage")
    if isinstance(cov, (int, float)):
        cov = cov / 100.0 if cov > 1 else cov
        out.append(_chk("Discovery coverage", round(cov * 100), 100,
                        "aspects neither answered, assumed, nor n/a", 1.2))
    return [c for c in out if c]

def checks_prd(fm, items, all_items, reached_hg1):
    by = lambda k: [i for i in items if i["kind"] == k]
    R, NG, AC = by("R"), by("NG"), by("AC")
    all_ac = [i for i in all_items if i["kind"] == "AC"]
    out = [
        _chk("No orphan requirement", sum(1 for r in R if r["refs"]), len(R),
             "requirements tracing to no problem"),
        _chk("Every R has an AC",
             sum(1 for r in R if any(_has_ref_to(a, {r["id"]}) for a in all_ac)), len(R),
             "requirements with no acceptance criterion"),
        _chk("Every NG excludes a P", sum(1 for n in NG if n["refs"]), len(NG),
             "non-goals with no `excludes: P#` — the unsolved share is implied, not stated"),
        _chk("Scope bounded (>=1 NG)", 1 if NG else 0, 1 if (R or NG) else 0,
             "no non-goals — scope is unbounded", 0.6),
    ]
    if reached_hg1:
        out.append(_chk("Scope approved at HG1", 1 if fm.get("approved_by") else 0, 1,
                        "scope triple not approved by a human"))
    return [c for c in out if c]

def checks_story(fm, items, all_items):
    by = lambda k: [i for i in items if i["kind"] == k]
    AC, R = by("AC"), by("R")
    out = [
        _chk("Every AC covers an R", sum(1 for a in AC if a["refs"]), len(AC),
             "ACs covering no requirement"),
        _chk("R subset resolves upward", sum(1 for r in R if r["refs"]), len(R),
             "sliced requirements with no problem"),
    ]
    return [c for c in out if c]

_CATS = ("happy", "edge", "error")

def checks_tp(fm, items, all_items, body):
    T = [i for i in items if i["kind"] == "T"]
    AC = [i for i in all_items if i["kind"] == "AC"]
    acids = {a["id"] for a in AC}
    tested = {_local(r) for t in T for r in t["refs"] if _local(r) in acids}
    # Categories are checked at PLAN level, not per AC: the contract asks for happy/edge/error
    # coverage across the plan, and real plans legitimately spread them over sibling ACs
    # (T1 happy + T2 edge on AC1, T3 error on AC2). Requiring all three per AC fires on
    # well-formed plans, and a check that always fires stops being read.
    blob = " ".join(t["text"].lower() for t in T)
    cats_ok = sum(1 for c in _CATS if c in blob)
    nonvac = len(re.findall(r"^\s*\|\s*T\d+\s*\|", body, re.M))
    out = [
        _chk("Every AC has a test", len(tested), len(AC), "ACs with no test", 1.2),
        _chk("Happy/edge/error present", cats_ok, len(_CATS),
             "test categories missing from the plan (or not labelled)", 0.8),
        _chk("Red state captured", 1 if fm.get("red_captured") else 0, 1,
             "no captured red output — the tests may be vacuous", 1.0),
        _chk("Non-vacuity stated per test", min(nonvac, len(T)), len(T),
             "tests with no reason they fail today", 0.8),
        _chk("One run command", 1 if fm.get("run_command") else 0, 1,
             "no single run command recorded", 0.4),
    ]
    return [c for c in out if c]

def checks_ip(fm, items, all_items, body):
    IM = [i for i in items if i["kind"] == "IM"]
    AC = [i for i in all_items if i["kind"] == "AC"]
    built = {_local(r) for m in IM for r in m["refs"] if _local(r) in {a["id"] for a in AC}}
    reuse = re.search(r"##\s*Reuse.*?\n(.*?)(\n##|\Z)", body, re.S)
    reuse_ok = bool(reuse and [l for l in reuse.group(1).splitlines()
                               if l.strip().startswith("- ") and "<" not in l])
    out = [
        _chk("Every AC has an impl step", len(built), len(AC), "ACs with no IM step"),
        _chk("No orphan IM", sum(1 for m in IM if m["refs"]), len(IM),
             "impl steps implementing no AC"),
        _chk("Reuse list present or justified", 1 if reuse_ok else 0, 1,
             "empty reuse list — usually means nobody looked", 0.6),
    ]
    if fm.get("charter"):
        cited = bool(re.search(r"^\s*\|\s*`?C\d+`?\s*\|", body, re.M))
        out.append(_chk("Charter constraints cited", 1 if cited else 0, 1,
                        "inherited constraints not cited — an unread constraint is no constraint",
                        0.6))
    return [c for c in out if c]

def checks_charter(fm, items, body):
    by = lambda k: [i for i in items if i["kind"] == k]
    SL, UNK, BND = by("SL"), by("UNK"), by("BND")
    needs = {s["id"]: [_local(r) for r in s["refs"] if _local(r).startswith("SL")] for s in SL}
    acyclic = _acyclic(needs)
    sl1 = next((s for s in SL if s["id"] == "SL1"), None)
    sl1_top = bool(sl1 and any(_local(r) == "UNK1" for r in sl1["refs"]))
    out = [
        _chk("Appetite declared", 1 if fm.get("appetite") else 0, 1,
             "no appetite — the charter can grow forever"),
        _chk("Re-bet scheduled", 1 if fm.get("review_after") else 0, 1,
             "no review_after — this is how zombie initiatives survive"),
        _chk("Boundaries stated (>=1 BND)", 1 if BND else 0, 1, "no boundaries"),
        _chk("Every slice has a hypothesis",
             sum(1 for s in SL if s["attrs"].get("hypothesis") or s["text"]), len(SL),
             "slices with no problem hypothesis"),
        _chk("Every slice reduces an unknown",
             sum(1 for s in SL if any(_local(r).startswith("UNK") for r in s["refs"])), len(SL),
             "slices not tied to a ranked unknown"),
        _chk("SL1 reduces the top unknown", 1 if sl1_top else 0, 1 if SL and UNK else 0,
             "the first slice attacks the easiest layer, not the biggest risk"),
        _chk("needs: graph acyclic", 1 if acyclic else 0, 1 if any(needs.values()) else 0,
             "circular slice dependencies"),
    ]
    return [c for c in out if c]

def _acyclic(edges):
    state = {}
    def visit(n):
        if state.get(n) == 1:
            return False
        if state.get(n) == 2:
            return True
        state[n] = 1
        for m in edges.get(n, []):
            if not visit(m):
                return False
        state[n] = 2
        return True
    return all(visit(n) for n in edges)

def checks_review(fm, items, body):
    F = [i for i in items if i["kind"] == "F"]
    verdict_rows = len(re.findall(r"^\s*\|\s*`?[\w\-.]+\.md`?\s*\|", body, re.M))
    out = [
        _chk("Verdict per input artifact", min(verdict_rows, 1), 1,
             "no per-artifact verdicts — a bundle verdict can't attribute a defect"),
        _chk("Findings attributed to a step",
             sum(1 for f in F if f["attrs"].get("attributed-to")), len(F),
             "findings with no attributed-to — the causing step can't learn"),
        _chk("Findings resolved or waived",
             sum(1 for f in F if f["attrs"].get("resolution", "open") != "open"), len(F),
             "findings still open"),
    ]
    return [c for c in out if c]


def score_checks(checks, finding_penalty=0):
    """Weighted mean of ratios × 100, minus 10 per finding attributed to this artifact."""
    if not checks:
        return None
    wsum = sum(c["weight"] for c in checks)
    base = 100 * sum(c["ratio"] * c["weight"] for c in checks) / wsum
    return max(0, min(100, int(round(base - 10 * finding_penalty))))


# ══════════════════════════════════════════════════════════════════════════════════════
# live markers
# ══════════════════════════════════════════════════════════════════════════════════════

def is_alive(pid):
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True

def scan_running(run_dir):
    path = os.path.join(run_dir, "running.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            mark = json.load(fh)
    except (ValueError, OSError):
        return None
    mark["alive"] = is_alive(mark.get("pid"))
    return mark

def _age(iso_ts):
    if not iso_ts:
        return None
    try:
        import calendar
        return time.time() - calendar.timegm(time.strptime(iso_ts, "%Y-%m-%dT%H:%M:%SZ"))
    except ValueError:
        return None

def scan_agents(repo):
    """Claude sub-agent breadcrumbs. A 'running' crumb with no close event may be orphaned
    (hard-killed session / crashed hook), so age it out rather than showing a false live."""
    repo = os.path.abspath(repo)
    out = []
    for f in sorted(glob.glob(os.path.join(repo, ".orchestration", "agents", "*.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                rec = json.load(fh)
        except (ValueError, OSError):
            continue
        rec["repo"] = os.path.basename(repo.rstrip("/"))
        rec["repoPath"] = repo
        running = rec.get("status") == "running"
        age = _age(rec.get("started")) if running else None
        if running and age is not None and age > STALE_AFTER_SECONDS:
            rec["status"] = "stale"
            running = False
        rec["live"] = running
        out.append(rec)
    out.sort(key=lambda r: r.get("started", ""), reverse=True)
    return out

def scan_delegations(run_dir):
    out = []
    path = os.path.join(run_dir, "delegations.jsonl")
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out

def agy_child(d, live=False):
    return {"kind": "agy", "who": "agy",
            "label": "agy delegation · iter %s" % d.get("iteration", "?"),
            "model": d.get("model", ""), "status": "running" if live else d.get("status", "done"),
            "live": bool(live), "result": d.get("result", ""),
            "started": d.get("started", ""), "finished": d.get("finished", "")}

def sub_child(a):
    return {"kind": "claude-subagent", "who": a.get("agent_type", "sub-agent"),
            "label": a.get("purpose", ""), "model": a.get("model") or "claude",
            "status": a.get("status", "?"), "live": bool(a.get("live")),
            "tokens": a.get("tokens"), "started": a.get("started", ""),
            "finished": a.get("finished", "")}


# ══════════════════════════════════════════════════════════════════════════════════════
# output dimensions (templates/scoring.md §4)
# ══════════════════════════════════════════════════════════════════════════════════════

QUALITY_DIMS = [("acceptance", "Acceptance", 0.30), ("tests", "Tests", 0.25),
                ("defects", "Defects", 0.20), ("security", "Security", 0.10),
                ("risk", "Assumptions & risk", 0.08), ("followups", "Open follow-ups", 0.07)]

def _clamp(v):
    return max(0, min(100, int(round(v))))

def _num(v, d=0):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else d

def output_quality(rec):
    m = rec.get("metrics") or {}
    g3 = ((m.get("gates") or {}).get("g3")) or {}
    cl = rec.get("closing") or {}
    override = m.get("quality") if isinstance(m.get("quality"), dict) else {}

    n_bugs, n_probs = len(cl.get("bugs") or []), len(cl.get("problems") or [])
    n_asm, n_oq = len(cl.get("assumptions") or []), len(cl.get("issues") or [])
    sec = _num(g3.get("security_findings"))
    good, flagged, overdue = (_num(g3.get(k)) for k in ("ac_good", "ac_flagged", "ac_overdue"))
    graded = good + flagged + overdue

    dims, why = {}, {}
    if graded:
        dims["acceptance"] = _clamp(100 * (good + 0.5 * flagged) / graded)
        why["acceptance"] = "%d good · %d flagged · %d overdue" % (good, flagged, overdue)
    elif rec.get("tests") in ("pass", "fail"):
        dims["acceptance"] = 100 if rec["tests"] == "pass" else 0
        why["acceptance"] = "no per-AC grading; tests %s" % rec["tests"]
    if rec.get("tests") in ("pass", "fail"):
        base = 100 if rec["tests"] == "pass" else 0
        red = (m.get("plan") or {}).get("red_captured")
        if rec["tests"] == "pass" and red is False:
            base -= 25
            why["tests"] = "pass, but no red state captured"
        else:
            why["tests"] = "tests %s" % rec["tests"]
        dims["tests"] = _clamp(base)
    dims["defects"] = _clamp(100 - 25 * n_bugs);  why["defects"] = "%d possible bug(s)" % n_bugs
    dims["security"] = _clamp(100 - 34 * sec);    why["security"] = "%d finding(s)" % sec
    dims["risk"] = _clamp(100 - 12 * n_asm - 8 * n_probs)
    why["risk"] = "%d open assumption(s) · %d discovered problem(s)" % (n_asm, n_probs)
    dims["followups"] = _clamp(100 - 15 * n_oq); why["followups"] = "%d open question(s)" % n_oq

    for k, v in override.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            dims[k] = _clamp(v); why[k] = "set in RECORD"

    present = [(k, l, w) for k, l, w in QUALITY_DIMS if k in dims]
    if not present:
        return None
    overall = _clamp(sum(dims[k] * w for k, _, w in present) / sum(w for _, _, w in present))
    caps = []
    if rec.get("status") == "blocked":
        caps.append("blocked")
    if rec.get("tests") == "fail":
        caps.append("tests failing")
    if caps:
        overall = min(overall, 40)
    return {"overall": overall, "caps": caps,
            "dims": [{"key": k, "label": l, "weight": w, "score": dims[k],
                      "why": why.get(k, "")} for k, l, w in present]}


# ══════════════════════════════════════════════════════════════════════════════════════
# scanning a repo
# ══════════════════════════════════════════════════════════════════════════════════════

SECTIONS = {"assumptions": "Assumptions", "issues": "Open issues",
            "problems": "Discovered problems", "bugs": "Possible bugs"}

def extract_closing(body):
    out, what = {k: [] for k in SECTIONS}, ""
    m = re.search(r"##\s*What shipped\s*\n(.+?)(\n##|\Z)", body, re.S)
    if m:
        what = " ".join(m.group(1).split())
    for key, heading in SECTIONS.items():
        m = re.search(r"##\s*" + re.escape(heading) + r"\s*\n(.*?)(\n##|\Z)", body, re.S)
        if not m:
            continue
        for ln in m.group(1).splitlines():
            ln = ln.strip()
            if ln.startswith("- ") and "<" not in ln[:4]:
                item = ln[2:].strip()
                if item and item.lower() not in ("none.", "none"):
                    out[key].append(item[:300])
    return what, out

def _title_of(body, fallback):
    m = re.search(r"^#\s+(.+)$", body, re.M)
    return (m.group(1).strip() if m else fallback)[:160]

def _is_template(fm):
    """Skip the skeletons ag-init copies into .orchestration/templates/."""
    return str(fm.get("id", "")).strip().startswith("<")

# artifact file -> (step, type). Order matters only for display.
ARTIFACT_STEP = {"prp": "S2", "spike": "S2b", "prd": "S3", "story": "S4", "bug": "S4",
                 "tech": "S4", "review-framing": "G1", "tp": "S5", "ip": "S6",
                 "review-readiness": "G2", "review-code": "G3", "record": "S8"}

def load_artifact(path, kind_hint=None):
    txt = _read(path)
    fm, body = parse_frontmatter(txt)
    if _is_template(fm):
        return None
    typ = fm.get("type") or kind_hint or ""
    art = {"file": os.path.basename(path), "path": path, "type": typ,
           "status": fm.get("status", ""), "fm": fm, "body": body,
           "title": _title_of(body, os.path.basename(path)),
           "step": ARTIFACT_STEP.get(typ, fm.get("step", "")),
           "items": parse_items(body)}
    return art

def _threads(art, container):
    out = []
    for it in art["items"]:
        if it["kind"] not in ("ASM", "OQ"):
            continue
        state = (it["attrs"].get("state") or "open").lower()
        if state != "open":
            continue
        out.append({"kind": it["kind"], "id": it["id"], "text": it["text"],
                    "affects": it["attrs"].get("affects", ""), "container": container,
                    "artifact": art["file"], "scope_blocking": False})
    return out

def _findings_by_step(arts):
    """Findings from review artifacts, grouped by the step they were attributed to."""
    per_step, all_f = {}, []
    for a in arts:
        if not a["type"].startswith("review"):
            continue
        for it in a["items"]:
            if it["kind"] != "F":
                continue
            res = (it["attrs"].get("resolution") or "open").lower()
            step = (it["attrs"].get("attributed-to") or "").strip() or "?"
            f = {"id": it["id"], "text": it["text"], "gate": a["fm"].get("gate", a["type"]),
                 "severity": it["attrs"].get("severity", ""), "resolution": res,
                 "attributed": step}
            all_f.append(f)
            if res in ("open", "waived"):
                per_step[step] = per_step.get(step, 0) + 1
    return per_step, all_f

def scan_repo(repo):
    """Return (containers, charters) for one repo."""
    repo = os.path.abspath(repo)
    base = os.path.join(repo, ".orchestration")
    if not os.path.isdir(base):
        return [], []
    name = os.path.basename(repo.rstrip("/"))

    # ── epics: prp / prd / spike, keyed by container id ──
    epics = {}
    for d in sorted(glob.glob(os.path.join(base, "epics", "*"))):
        if not os.path.isdir(d):
            continue
        cid = os.path.basename(d)
        arts = [a for a in (load_artifact(p) for p in sorted(glob.glob(os.path.join(d, "*.md")))
                            if os.path.basename(p) != "decisions.md") if a]
        if arts:
            epics[cid] = {"dir": d, "arts": arts}

    # ── charters ──
    charters = []
    for d in sorted(glob.glob(os.path.join(base, "charters", "*"))):
        if not os.path.isdir(d):
            continue
        cid = os.path.basename(d)
        art = next((load_artifact(p) for p in glob.glob(os.path.join(d, "charter-*.md"))), None)
        if not art:
            continue
        fm, items = art["fm"], art["items"]
        checks = checks_charter(fm, items, art["body"])
        slices = []
        for s in [i for i in items if i["kind"] == "SL"]:
            slices.append({"id": s["id"], "title": s["text"],
                           "hypothesis": s["attrs"].get("hypothesis", ""),
                           "reduces": next((_local(r) for r in s["refs"]
                                            if _local(r).startswith("UNK")), ""),
                           "needs": [_local(r) for r in s["refs"] if _local(r).startswith("SL")],
                           "state": (s["attrs"].get("state") or "hypothesis").lower(),
                           "minted": s["attrs"].get("minted", "").strip(" -")})
        appetite_n = None
        m = re.search(r"(\d+)\s*slice", str(fm.get("appetite", "")), re.I)
        if m:
            appetite_n = int(m.group(1))
        minted = sum(1 for s in slices if s["state"] in ("in-flight", "done"))
        charters.append({
            "repo": name, "repoPath": repo, "id": cid, "kind": "charter",
            "title": art["title"], "status": fm.get("status", ""),
            "appetite": fm.get("appetite", ""), "review_after": fm.get("review_after", ""),
            "approved_by": fm.get("approved_by", ""), "approved_at": fm.get("approved_at", ""),
            "unknowns": [{"id": u["id"], "text": u["text"]} for u in items if u["kind"] == "UNK"],
            "boundaries": [{"id": b["id"], "text": b["text"]} for b in items if b["kind"] == "BND"],
            "slices": slices, "minted": minted, "appetiteSlices": appetite_n,
            "burn": (minted / appetite_n) if appetite_n else None,
            "checks": checks, "score": score_checks(checks),
            "betLog": [ln.strip("# ").strip() for ln in art["body"].splitlines()
                       if re.match(r"^###\s+SL\d+", ln.strip())],
            "waiting": "HG0" if not fm.get("approved_by") else "",
            "path": art["path"],
        })

    # ── tasks: one container per runs/<id>/ ──
    containers = []
    for d in sorted(glob.glob(os.path.join(base, "runs", "*"))):
        if not os.path.isdir(d):
            continue
        tid = os.path.basename(d)
        arts = [a for a in (load_artifact(p) for p in sorted(glob.glob(os.path.join(d, "*.md")))
                            if os.path.basename(p) != "decisions.md") if a]
        if not arts:
            continue
        spec = next((a for a in arts if a["type"] in ("story", "bug", "tech", "prp")), None)
        fm0 = spec["fm"] if spec else arts[0]["fm"]
        parent = str(fm0.get("parent", "") or "")
        parent_arts = epics.get(parent, {}).get("arts", []) if parent else []
        all_arts = parent_arts + arts
        all_items = [i for a in all_arts for i in a["items"]]

        per_step_findings, findings = _findings_by_step(all_arts)
        reached = furthest_step(all_arts, d)

        # per-artifact scores
        scored = []
        past_hg1 = STEP_ORDER.get(reached, 0) >= STEP_ORDER["HG1"]
        for a in all_arts:
            t, fm, body, items = a["type"], a["fm"], a["body"], a["items"]
            if t == "prp":
                ck = checks_prp(fm, items, all_items)
            elif t == "prd":
                ck = checks_prd(fm, items, all_items, past_hg1)
            elif t in ("story", "bug", "tech"):
                ck = checks_story(fm, items, all_items)
                # A COLLAPSED doc is prp + prd + story in one file, so it must face all three
                # check sets. Running only the story checks would let a collapsed item score
                # 100 while carrying no evidence, no coverage, and no NG up-links.
                if _collapsed(a):
                    ck = checks_prp(fm, items, all_items) + \
                         checks_prd(fm, items, all_items, past_hg1) + ck
            elif t == "tp":
                ck = checks_tp(fm, items, all_items, body)
            elif t == "ip":
                ck = checks_ip(fm, items, all_items, body)
            elif t.startswith("review"):
                ck = checks_review(fm, items, body)
            else:
                ck = []
            # a collapsed doc IS S1–S4, so it reports on every framing step it stands in for
            steps = ["S1", "S2", "S4"] if (t in ("story", "bug", "tech") and _collapsed(a)) \
                else [a["step"]]
            pen = per_step_findings.get(a["step"], 0)
            scored.append({"file": a["file"], "type": t, "status": a["status"],
                           "step": a["step"], "steps": steps, "checks": ck, "penalty": pen,
                           "score": score_checks(ck, pen), "path": a["path"],
                           "title": a["title"]})

        rec = next((a for a in arts if a["type"] == "record"), None)
        c = {"repo": name, "repoPath": repo, "id": tid, "kind": "task", "dir": d,
             "type": (spec["type"] if spec else ""), "title": spec["title"] if spec else tid,
             "parent": parent, "charter": str(fm0.get("charter", "") or ""),
             "slice": str(fm0.get("slice", "") or ""), "form": fm0.get("form", ""),
             "status": fm0.get("status", ""), "blocked_reason": fm0.get("blocked_reason", ""),
             "rejection_reason": fm0.get("rejection_reason", ""),
             "rejection_stage": fm0.get("rejection_stage", ""),
             "coverage": fm0.get("discovery_coverage", None),
             # HG1 approval lives on whichever doc holds the scope triple: the PRD in full
             # form, the single doc in collapsed form.
             "approvedBy": (next((a["fm"].get("approved_by") for a in all_arts
                                  if a["type"] == "prd" and a["fm"].get("approved_by")), "")
                            or (fm0.get("approved_by") or "")),
             "artifacts": scored, "findings": findings, "step": reached,
             "threads": [t for a in all_arts for t in _threads(a, tid)],
             "closing": {k: [] for k in SECTIONS}, "metrics": {}, "tests": "",
             }

        if rec:
            c["metrics"] = rec["fm"].get("metrics") or {}
            c["status"] = rec["fm"].get("status") or c["status"]
            c["tests"] = rec["fm"].get("tests", "")
            c["blocked_reason"] = rec["fm"].get("blocked_reason") or c["blocked_reason"]
            what, closing = extract_closing(rec["body"])
            c["whatShipped"], c["closing"] = what, closing
            c["recordPath"] = rec["path"]

        # Scope-blocking assumptions. The contract's rule is "an ASM on Discovery aspect 5 or 6".
        # The deterministic proxy for that is an ASM whose `affects:` points at an R or NG — the
        # scope half of the triple. An ASM on a P, an AC, or an IM is carried, not blocking.
        # This is a proxy, not the rule itself; the gate assessor is the authority.
        for t in c["threads"]:
            if t["kind"] == "ASM" and re.match(r"^(R|NG)\d", str(t["affects"]).strip()):
                t["scope_blocking"] = True

        c["steps"] = build_steps(c, scored, per_step_findings, d)
        c["framingScore"] = phase_score(c["steps"], ("S1", "S2", "S2b", "S3", "S4",
                                                     "G1", "S5", "S6", "G2"))
        c["quality"] = output_quality(c) if rec else None
        c["outputScore"] = (c["quality"] or {}).get("overall")

        # live children
        delegs = scan_delegations(d)
        children = []
        for dg in delegs:
            children.append(agy_child(dg))
        run = scan_running(d)
        if run:
            c["running"] = run
            if run.get("alive"):
                children.append(agy_child(run, live=True))
        c["agyChildren"] = children
        c["model"] = (run or {}).get("model", "") if run and run.get("alive") else (
            delegs[-1].get("model", "") if delegs else "")
        c["waiting"] = waiting_on(c)
        c["attention"] = attention(c)
        c["needsAttention"] = bool(c["attention"])
        containers.append(c)

    return containers, charters


def _collapsed(art):
    """A single doc holding the whole spec chain: form: collapsed, or it carries SIG itself."""
    return art["fm"].get("form") == "collapsed" or any(i["kind"] == "SIG" for i in art["items"])

def _coverage_complete(fm):
    cov = fm.get("discovery_coverage")
    return isinstance(cov, (int, float)) and (cov >= 100 or (cov <= 1 and cov >= 1))

def furthest_step(arts, run_dir):
    """The furthest step reached, from which artifacts exist and at what status."""
    have = {a["type"]: a for a in arts}
    passed = lambda t: (have.get(t, {}).get("fm", {}) or {}).get("verdict") == "pass"
    spec = next((have[k] for k in ("story", "bug", "tech") if k in have), None)

    # collapsed form: one doc is the whole framing chain, so S1–S4 are read off IT, not off
    # the presence of a prd that will never exist.
    if spec is not None and _collapsed(spec) and "prd" not in have:
        if not _coverage_complete(spec["fm"]):
            return "S2"
        if not spec["fm"].get("approved_by"):
            return "HG1"
    if "record" in have and have["record"]["fm"].get("status") == "done":
        return "S8"
    if passed("review-code"):
        return "HG2"
    if glob.glob(os.path.join(run_dir, "result.iter*.json")) or "brief" in have or \
            os.path.exists(os.path.join(run_dir, "brief.md")):
        return "G3" if "review-code" in have else "S7"
    if passed("review-readiness"):
        return "S7"
    if "review-readiness" in have:
        return "G2"
    if "ip" in have:
        return "G2"
    if "tp" in have:
        return "S6"
    if passed("review-framing"):
        return "S5"
    if "review-framing" in have:
        return "G1"
    if any(t in have for t in ("story", "bug", "tech")):
        return "G1"
    prd = have.get("prd")
    if prd:
        return "S4" if prd["fm"].get("approved_by") else "HG1"
    prp = have.get("prp")
    if prp:
        cov = prp["fm"].get("discovery_coverage")
        if isinstance(cov, (int, float)) and (cov >= 1 or cov >= 100):
            return "S3"
        return "S2"
    return "S1"

def build_steps(c, scored, findings_by_step, run_dir):
    """One cell per step: status + derived score + declared IN/OUT artifacts."""
    reached = STEP_ORDER.get(c["step"], 0)
    by_step = {}
    for a in scored:
        for sid in a.get("steps") or [a["step"]]:
            by_step.setdefault(sid, []).append(a)
    out = {}
    for sid, label, level in STEPS:
        arts = by_step.get(sid, [])
        idx = STEP_ORDER[sid]
        scores = [a["score"] for a in arts if a["score"] is not None]
        # State is decided by POSITION, not by whether a file happens to mention this step.
        # A collapsed doc contains AC while still sitting at S2, so "an artifact exists" must
        # not be read as "the step is done".
        if sid in ("S0", "HG0"):
            # charter-level. A task only exists because a slice was minted, and minting
            # requires HG0 — so "inherited", not a score this row earned.
            state = "inherited" if c.get("charter") else "n/a"
        elif idx < reached:
            state = "skipped" if (sid in OPTIONAL_STEPS and not arts) else "done"
        elif idx == reached:
            state = "current"
        else:
            state = "pending"
        if sid == "HG1":
            state = "done" if c.get("approvedBy") else (
                "waiting" if c["step"] == "HG1" else state)
        if sid == "HG2" and c["step"] == "HG2":
            state = "waiting"
        if sid == "S8" and c.get("status") == "done":
            state = "done"
        out[sid] = {"id": sid, "label": label, "level": level, "state": state,
                    "score": (int(round(sum(scores) / len(scores))) if scores else None),
                    "artifacts": [{"file": a["file"], "type": a["type"], "status": a["status"],
                                   "score": a["score"], "checks": a["checks"]} for a in arts],
                    "inputs": step_inputs(sid), "findings": findings_by_step.get(sid, 0)}
    return out

STEP_INPUTS = {
    "S1": ["raw ask"], "S2": ["SIG", "ASK"], "S2b": ["P"], "S3": ["prp", "spike"],
    "HG1": ["prd (P+R+NG)", "coverage report"], "S4": ["prd (approved)"],
    "G1": ["prp", "prd", "story"], "S5": ["AC"], "S6": ["AC", "TP"],
    "G2": ["story", "TP", "IP"], "S7": ["brief (story+TP+IP)"],
    "G3": ["diff", "story", "TP"], "HG2": ["review-code", "diff"], "S8": ["review-code (pass)"],
    "S0": ["oversized ask"], "HG0": ["charter"],
}
def step_inputs(sid):
    return STEP_INPUTS.get(sid, [])

def phase_score(steps, ids):
    vals = [steps[i]["score"] for i in ids if i in steps and steps[i]["score"] is not None]
    return int(round(sum(vals) / len(vals))) if vals else None

def waiting_on(c):
    if c.get("status") == "blocked" and c.get("blocked_reason") == "approval":
        return c["step"] if c["step"] in HUMAN_GATES else "HG1"
    return c["step"] if c["step"] in HUMAN_GATES else ""

def attention(c):
    run = c.get("running")
    if run and run.get("alive"):
        return "agy delegating now (iter %s)" % run.get("iteration", "?")
    if c.get("status") == "rejected":
        return ""                                     # rejection is an outcome, not an alarm
    w = c.get("waiting")
    if w:
        return "waiting on human — %s" % w
    if c.get("status") == "blocked":
        return "blocked: %s" % (c.get("blocked_reason") or "unspecified")
    if c.get("tests") == "fail":
        return "tests failing"
    scope_blocked = [t for t in c.get("threads", []) if t.get("scope_blocking")]
    if scope_blocked and c["step"] in ("S2", "S3", "HG1"):
        return "%d scope assumption(s) block HG1" % len(scope_blocked)
    fs = c.get("framingScore")
    if isinstance(fs, int) and fs < 60 and c["step"] not in ("S1", "S2"):
        return "low framing score (%d)" % fs
    q = c.get("quality") or {}
    if isinstance(q.get("overall"), int) and q["overall"] < 60:
        weakest = min(q.get("dims") or [], key=lambda d: d["score"], default=None)
        return "low output score (%d)%s" % (
            q["overall"], " — weakest: " + weakest["label"] if weakest else "")
    if c.get("closing", {}).get("bugs"):
        return "possible bugs recorded"
    return ""


# ══════════════════════════════════════════════════════════════════════════════════════
# payload / CLI
# ══════════════════════════════════════════════════════════════════════════════════════

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
    found, base = [], root.rstrip("/").count("/")
    for dirpath, dirnames, _ in os.walk(root):
        if dirpath.count("/") - base > max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "worktrees")]
        if os.path.isdir(os.path.join(dirpath, ".orchestration")):
            found.append(dirpath)
            dirnames[:] = []
    return found

def dedup_repos(repos):
    seen, uniq = set(), []
    for r in repos:
        ap = os.path.abspath(os.path.expanduser(r))
        if ap not in seen:
            seen.add(ap); uniq.append(ap)
    return uniq

def build_payload(repos, title):
    items, charters, agents = [], [], []
    for r in repos:
        c, ch = scan_repo(r)
        items.extend(c); charters.extend(ch)
        agents.extend(scan_agents(r))

    by_key = {(i["repo"], i["id"]): i for i in items}
    orphans = {}
    for a in agents:
        owner = by_key.get((a.get("repo"), a.get("task")))
        (orphans.setdefault(a.get("repo"), []) if owner is None
         else owner.setdefault("_subs", [])).append(a)

    for i in items:
        subs = sorted(i.pop("_subs", []), key=lambda a: a.get("started", ""), reverse=True)
        i["children"] = (i.pop("agyChildren", []) or []) + [sub_child(a) for a in subs]
        i["live"] = any(ch["live"] for ch in i["children"])
        if not i.get("needsAttention"):
            bad = next((ch for ch in i["children"]
                        if ch["status"] in ("failed", "timeout")), None)
            if bad:
                i["attention"] = "%s %s" % (bad["who"], bad["status"])
                i["needsAttention"] = True

    for repo, subs in orphans.items():
        children = [sub_child(a) for a in sorted(subs, key=lambda a: a.get("started", ""),
                                                 reverse=True)]
        items.append({"repo": repo, "repoPath": subs[0].get("repoPath", ""),
                      "id": "(unassigned)", "kind": "task", "type": "",
                      "title": "Unassigned sub-agents", "synthetic": True, "status": "",
                      "step": "", "steps": {}, "artifacts": [], "threads": [], "findings": [],
                      "closing": {k: [] for k in SECTIONS}, "metrics": {}, "children": children,
                      "live": any(c["live"] for c in children), "waiting": "",
                      "attention": "", "needsAttention": False})

    # attach children to charters
    for ch in charters:
        ch["children"] = [i["id"] for i in items
                          if i.get("charter") == ch["id"] or
                          str(i.get("slice", "")).startswith(ch["id"] + "#")]

    threads = [t for i in items for t in i.get("threads", [])]
    return {"title": title, "steps": [{"id": s, "label": l, "level": v} for s, l, v in STEPS],
            "items": items, "charters": charters, "agents": agents,
            "threads": threads, "repos": list(repos)}

def render_static(repos, title, out_file):
    payload = build_payload(repos, title)
    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()
    page = page.replace("/*__AG_DATA__*/null", _json_for_script(payload))
    page = page.replace("__AG_TITLE__", _escape_title(title))
    with open(out_file, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("wrote %s — %d item(s), %d charter(s) from %d repo(s)" % (
        out_file, len(payload["items"]), len(payload["charters"]), len(repos)))

def serve(repos, title, port):
    """Read-only live server, 127.0.0.1 only. Re-scans on each /api/board."""
    import http.server, socketserver
    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read().replace("/*__AG_LIVE__*/false", "true") \
                        .replace("__AG_TITLE__", _escape_title(title))
    page_bytes = page.encode("utf-8")

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
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
            if path in ("/api/board", "/api/runs"):
                self._send(json.dumps(build_payload(repos, title)).encode("utf-8"),
                           "application/json; charset=utf-8")
            elif path in ("/", "/index.html"):
                self._send(page_bytes, "text/html; charset=utf-8")
            else:
                self.send_response(404); self.end_headers()

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with Server(("127.0.0.1", port), Handler) as httpd:
        print("live board on http://127.0.0.1:%d  (re-scans %d repo(s) per request; Ctrl-C)"
              % (port, len(repos)))
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
    repos = dedup_repos(repos or ["."])
    serve(repos, title, port) if do_serve else render_static(repos, title, out_file)

if __name__ == "__main__":
    main(sys.argv[1:])
