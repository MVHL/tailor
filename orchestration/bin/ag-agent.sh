#!/usr/bin/env bash
#
# ag-agent.sh — Gap B: make Claude Code sub-agent spawns visible to the board.
#
# Claude sub-agents (the Task/Agent tool: Explore, Plan, general-purpose, …) live
# only inside the Claude Code session and leave no artifact under .orchestration/,
# so the dashboard cannot see them. This helper lets the Conductor drop a small
# JSON breadcrumb per spawn — one file under .orchestration/agents/ — which the
# board renders alongside agy delegations. The breadcrumb is PERMANENT (an audit
# record); its `status` moves running → done|failed. Contrast with agy's transient
# running.json, which is deleted on exit.
#
# Usage:
#   ag-agent.sh start --type <agentType> --purpose "<text>" \
#                     [--task <run-id>] [--repo <path>] [--model <name>] [--id <id>]
#   ag-agent.sh done  <id> [--repo <path>] [--status done|failed] [--note "<text>"]
#   ag-agent.sh list  [--repo <path>]
#
# `start` prints:  AG_AGENT_ID=<id>  and  AG_AGENT_FILE=<path>
# Capture the id and pass it to `done` when the sub-agent returns.
#
# Repo defaults to `git rev-parse --show-toplevel` of the current directory.

set -euo pipefail

die() { echo "ag-agent.sh: $*" >&2; exit 2; }
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

resolve_repo() {
  if [ -n "${1:-}" ]; then printf '%s' "$1"; return; fi
  git rev-parse --show-toplevel 2>/dev/null || die "not in a git repo; pass --repo"
}

slug() { printf '%s' "$1" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-' ; }

cmd_start() {
  local type="" purpose="" task="" repo="" model="" id=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --type)    type="${2:-}"; shift 2 ;;
      --purpose) purpose="${2:-}"; shift 2 ;;
      --task)    task="${2:-}"; shift 2 ;;
      --repo)    repo="${2:-}"; shift 2 ;;
      --model)   model="${2:-}"; shift 2 ;;
      --id)      id="${2:-}"; shift 2 ;;
      *) die "start: unknown argument: $1" ;;
    esac
  done
  [ -n "$type" ]    || die "start: --type is required"
  [ -n "$purpose" ] || die "start: --purpose is required"
  repo="$(resolve_repo "$repo")"
  local dir="$repo/.orchestration/agents"
  mkdir -p "$dir"
  if [ -z "$id" ]; then
    id="$(slug "$type")-$(date -u +%Y%m%d-%H%M%S)-$$"
  fi
  local file="$dir/$id.json"
  local started; started="$(now)"
  python3 - "$file" "$id" "$type" "$task" "$purpose" "$model" "$started" <<'PY'
import json, sys
file, _id, atype, task, purpose, model, started = sys.argv[1:8]
rec = {"kind":"claude-subagent","id":_id,"agent_type":atype,"task":task,
       "purpose":purpose,"model":model,"status":"running",
       "started":started,"finished":"","note":""}
with open(file,"w",encoding="utf-8") as fh:
    json.dump(rec, fh, ensure_ascii=False, indent=2)
PY
  echo "AG_AGENT_ID=$id"
  echo "AG_AGENT_FILE=$file"
}

cmd_done() {
  local id="" repo="" status="done" note=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --repo)   repo="${2:-}"; shift 2 ;;
      --status) status="${2:-}"; shift 2 ;;
      --note)   note="${2:-}"; shift 2 ;;
      --id)     id="${2:-}"; shift 2 ;;
      -*)       die "done: unknown argument: $1" ;;
      *)        id="$1"; shift ;;
    esac
  done
  [ -n "$id" ] || die "done: agent id is required (positional or --id)"
  case "$status" in done|failed) ;; *) die "done: --status must be done|failed" ;; esac
  repo="$(resolve_repo "$repo")"
  local file="$repo/.orchestration/agents/$id.json"
  [ -f "$file" ] || die "done: no breadcrumb for id '$id' ($file)"
  local finished; finished="$(now)"
  python3 - "$file" "$status" "$finished" "$note" <<'PY'
import json, sys
file, status, finished, note = sys.argv[1:5]
with open(file, encoding="utf-8") as fh:
    rec = json.load(fh)
rec["status"] = status
rec["finished"] = finished
if note:
    rec["note"] = note
with open(file, "w", encoding="utf-8") as fh:
    json.dump(rec, fh, ensure_ascii=False, indent=2)
PY
  echo "AG_AGENT_ID=$id"
  echo "AG_AGENT_STATUS=$status"
}

cmd_list() {
  local repo=""
  while [ $# -gt 0 ]; do
    case "$1" in --repo) repo="${2:-}"; shift 2 ;; *) die "list: unknown argument: $1" ;; esac
  done
  repo="$(resolve_repo "$repo")"
  local dir="$repo/.orchestration/agents"
  [ -d "$dir" ] || { echo "(no sub-agents recorded)"; return; }
  python3 - "$dir" <<'PY'
import json, glob, os, sys
dir = sys.argv[1]
files = sorted(glob.glob(os.path.join(dir, "*.json")))
if not files:
    print("(no sub-agents recorded)"); raise SystemExit
for f in files:
    try:
        r = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    print(f"{r.get('status','?'):8} {r.get('agent_type','?'):16} "
          f"{r.get('task') or '-':18} {r.get('id','?')}  {r.get('purpose','')[:60]}")
PY
}

[ $# -ge 1 ] || die "usage: ag-agent.sh {start|done|list} …"
sub="$1"; shift
case "$sub" in
  start) cmd_start "$@" ;;
  done)  cmd_done "$@" ;;
  list)  cmd_list "$@" ;;
  -h|--help) sed -n '2,32p' "$0" ;;
  *) die "unknown subcommand: $sub" ;;
esac
