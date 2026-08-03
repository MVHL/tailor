#!/usr/bin/env python3
"""
ag-agent-hook.py — Gap B, automatic. A Claude Code hook that records every
sub-agent (Task/Agent) spawn as a breadcrumb under .orchestration/agents/, so the
board's "Live now" panel and "Sub-agents" table populate WITHOUT the Conductor
remembering to call ag-agent.sh by hand.

Wire it in .claude/settings.json to three events (see orchestration/README.md):
  - PreToolUse  on the sub-agent tool  -> writes a "running" breadcrumb
  - PostToolUse on the sub-agent tool  -> flips the match to "done"/"failed"
  - SubagentStop                        -> FIFO fallback to close a running one

It is deliberately tool-NAME-agnostic: it acts only when tool_input carries a
`subagent_type`, so it works whether the tool is called `Task` or `Agent`. It writes
only inside an already-onboarded repo (one with a .orchestration/ dir) and never fails
the session — any error is swallowed and the hook exits 0.

Correlation: uses `tool_use_id` if the event provides one (exact Pre<->Post match),
else matches on subagent_type+description among running breadcrumbs (FIFO), else
(SubagentStop) closes the oldest running hook-sourced breadcrumb.
"""
import sys, os, json, glob, subprocess, time

def read_event():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def git_root(cwd):
    try:
        r = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None

def sanitize(s):
    return "".join(c if (c.isalnum() or c in "-_") else "-" for c in str(s))[:80]

def agents_dir(repo):
    return os.path.join(repo, ".orchestration", "agents")

def current_task(repo):
    p = os.path.join(repo, ".orchestration", "current-task")
    try:
        if os.path.exists(p):
            return open(p, encoding="utf-8").read().strip()
    except Exception:
        pass
    return ""

def _purpose(ti):
    return (ti.get("description") or (ti.get("prompt", "") or "")[:80] or "").strip()

def start(data, repo, ti):
    d = agents_dir(repo)
    os.makedirs(d, exist_ok=True)
    tuid = data.get("tool_use_id") or ""
    atype = ti.get("subagent_type") or "subagent"
    purpose = _purpose(ti)
    if tuid:
        _id = "hook-" + sanitize(tuid)
    else:
        _id = "hook-%s-%s-%d" % (sanitize(atype),
                                 time.strftime("%Y%m%d-%H%M%S", time.gmtime()), os.getpid())
    rec = {"kind": "claude-subagent", "id": _id, "agent_type": atype,
           "task": current_task(repo), "purpose": purpose, "model": "",
           "status": "running", "started": now(), "finished": "", "note": "",
           "source": "hook", "_tuid": tuid, "_match": atype + "|" + purpose}
    with open(os.path.join(d, _id + ".json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)

def _running(d, pred):
    out = []
    for f in glob.glob(os.path.join(d, "*.json")):
        try:
            r = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if r.get("status") == "running" and pred(r):
            out.append((r.get("started", ""), f, r))
    out.sort(key=lambda t: t[0])   # oldest first (FIFO)
    return out

def finish(data, repo, ti):
    d = agents_dir(repo)
    if not os.path.isdir(d):
        return
    tuid = data.get("tool_use_id") or ""
    status = "done"
    tokens = None
    tr = data.get("tool_response")
    if isinstance(tr, dict):
        if tr.get("is_error") or tr.get("error"):
            status = "failed"
        usage = tr.get("usage")
        if isinstance(usage, dict):
            tokens = usage.get("output_tokens")

    target = None
    if tuid:
        p = os.path.join(d, "hook-" + sanitize(tuid) + ".json")
        if os.path.exists(p):
            target = p
    if target is None and isinstance(ti, dict) and ti.get("subagent_type"):
        m = (ti.get("subagent_type") or "") + "|" + _purpose(ti)
        cands = _running(d, lambda r: r.get("_match") == m)
        if cands:
            target = cands[0][1]
    if target is None:
        cands = _running(d, lambda r: r.get("source") == "hook")
        if cands:
            target = cands[0][1]
    if not target:
        return
    try:
        r = json.load(open(target, encoding="utf-8"))
        r["status"] = status
        r["finished"] = now()
        if tokens is not None:
            r["tokens"] = tokens
        with open(target, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def main():
    data = read_event()
    event = data.get("hook_event_name") or ""
    ti = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    repo = git_root(cwd) or cwd
    if not os.path.isdir(os.path.join(repo, ".orchestration")):
        return   # only touch onboarded repos
    is_subagent = "subagent_type" in ti
    if event == "PreToolUse" and is_subagent:
        start(data, repo, ti)
    elif event == "PostToolUse" and is_subagent:
        finish(data, repo, ti)
    elif event == "SubagentStop":
        finish(data, repo, ti)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)   # never block or fail the session
