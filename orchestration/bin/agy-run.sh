#!/usr/bin/env bash
#
# agy-run.sh — the single choke point for delegating implementation to the
# Antigravity CLI (agy). Claude Code (the Conductor) never calls `agy` directly;
# it calls this adapter so that logging, timeouts, workspace scoping, structured
# output and conversation continuity all live in one place.
#
# Confirmed against agy v1.1.9 (`agy --help`).
#
# Usage:
#   agy-run.sh --brief <file> --dir <workspace> --run-dir <run-dir> [options]
#
# Required:
#   --brief   <file>   Prompt/spec file handed to agy (the P/R/AC + TP + IP brief).
#   --dir     <path>   Workspace directory agy operates in (normally a git worktree).
#   --run-dir <path>   Where transcript.log / result.json / conversation.id are written.
#
# Options:
#   --model     <name>  agy model (default: gemini-3.6-flash-high — Flash is much faster
#                       and cheaper than Pro; drop to -medium/-low for even less). See
#                       `agy models`.
#                       NOTE: most model names already encode the effort tier
#                       (e.g. -high/-low), so --effort is left unset by default.
#   --effort    <lvl>   low|medium|high. Only for models whose name does NOT
#                       already carry a tier (e.g. claude-sonnet-4-6). Passing it
#                       alongside a tier-suffixed model is an agy error.
#   --timeout   <dur>   Go duration for --print-timeout (default: 15m).
#   --continue  <id>    Resume a prior agy conversation by ID (review→fix loop).
#   --iteration <n>     Iteration label for the transcript (default: 1).
#   --sandbox           Pass --sandbox to agy (terminal restrictions on).
#   --no-skip-perms     Do NOT pass --dangerously-skip-permissions (agy will block
#                       on permission prompts; only use interactively).
#
# Output (stdout, one KEY=VALUE per line — parse these):
#   AGY_EXIT=<int>            agy process exit code (124 = timed out)
#   AGY_RESULT_JSON=<path>    raw JSON envelope from agy (--output-format json)
#   AGY_TRANSCRIPT=<path>     human-readable transcript for this iteration
#   AGY_CONVERSATION=<id|">   conversation id if one could be extracted (for --continue)
#   AGY_RESULT_TEXT=<path>    best-effort extracted final message text
#
# Notes:
#  * The git diff and the test run are the SOURCE OF TRUTH for correctness.
#    The JSON envelope is for monitoring/audit, not for trusting agy's self-report.
#  * --dangerously-skip-permissions is ON by default because a headless loop
#    cannot answer prompts. It is confined to --dir (a throwaway worktree). Keep
#    that worktree free of secrets.

set -euo pipefail

BRIEF="" DIR="" RUN_DIR=""
MODEL="gemini-3.6-flash-high"
EFFORT=""   # unset by default; model name carries the tier
TIMEOUT="15m"
CONTINUE=""
ITER="1"
SANDBOX=0
SKIP_PERMS=1

die() { echo "agy-run.sh: $*" >&2; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --brief)         BRIEF="${2:-}"; shift 2 ;;
    --dir)           DIR="${2:-}"; shift 2 ;;
    --run-dir)       RUN_DIR="${2:-}"; shift 2 ;;
    --model)         MODEL="${2:-}"; shift 2 ;;
    --effort)        EFFORT="${2:-}"; shift 2 ;;
    --timeout)       TIMEOUT="${2:-}"; shift 2 ;;
    --continue)      CONTINUE="${2:-}"; shift 2 ;;
    --iteration)     ITER="${2:-}"; shift 2 ;;
    --sandbox)       SANDBOX=1; shift ;;
    --no-skip-perms) SKIP_PERMS=0; shift ;;
    -h|--help)       sed -n '2,40p' "$0"; exit 0 ;;
    *)               die "unknown argument: $1" ;;
  esac
done

[ -n "$BRIEF" ]   || die "--brief is required"
[ -n "$DIR" ]     || die "--dir is required"
[ -n "$RUN_DIR" ] || die "--run-dir is required"
[ -f "$BRIEF" ]   || die "brief file not found: $BRIEF"
[ -d "$DIR" ]     || die "workspace dir not found: $DIR"
command -v agy >/dev/null 2>&1 || die "agy not found on PATH"

mkdir -p "$RUN_DIR"
TRANSCRIPT="$RUN_DIR/transcript.log"
RESULT_JSON="$RUN_DIR/result.iter${ITER}.json"
RESULT_TEXT="$RUN_DIR/result.iter${ITER}.txt"
CONV_FILE="$RUN_DIR/conversation.id"
RUNNING="$RUN_DIR/running.json"

# --- Gap A: live-run marker -------------------------------------------------
# The dashboard reads running.json to show a delegation that is running NOW.
# It is written just before agy starts and removed on ANY exit (success, timeout,
# kill), so "file present + pid alive" == running, and "file absent" == not running.
json_str() { printf '%s' "${1:-}" | sed 's/\\/\\\\/g; s/"/\\"/g'; }
cleanup_running() { rm -f "$RUNNING" 2>/dev/null || true; }
trap cleanup_running EXIT INT TERM
TASK_ID="$(basename "$RUN_DIR")"

# Build agy args.
AGY_ARGS=( --print "$(cat "$BRIEF")"
           --add-dir "$DIR"
           --model "$MODEL"
           --mode accept-edits
           --output-format json
           --print-timeout "$TIMEOUT"
           --disable-slash-commands )
[ -n "$EFFORT" ] && AGY_ARGS+=( --effort "$EFFORT" )
[ "$SKIP_PERMS" -eq 1 ] && AGY_ARGS+=( --dangerously-skip-permissions )
[ "$SANDBOX" -eq 1 ]    && AGY_ARGS+=( --sandbox )
if [ -n "$CONTINUE" ]; then
  AGY_ARGS+=( --conversation "$CONTINUE" )
elif [ -f "$CONV_FILE" ]; then
  # Auto-resume the run's own conversation on subsequent iterations.
  AGY_ARGS+=( --conversation "$(cat "$CONV_FILE")" )
fi

STARTED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Publish the live marker now — agy is about to run.
printf '{"kind":"agy","task":"%s","pid":%d,"model":"%s","effort":"%s","iteration":"%s","workspace":"%s","brief":"%s","started":"%s","continue":"%s"}\n' \
  "$(json_str "$TASK_ID")" "$$" "$(json_str "$MODEL")" "$(json_str "$EFFORT")" \
  "$(json_str "$ITER")" "$(json_str "$DIR")" "$(json_str "$BRIEF")" \
  "$STARTED" "$(json_str "$CONTINUE")" > "$RUNNING"

{
  echo "===================================================================="
  echo "AGY ITERATION $ITER  |  model=$MODEL effort=$EFFORT timeout=$TIMEOUT"
  echo "workspace=$DIR"
  [ -n "$CONTINUE" ] && echo "resuming conversation=$CONTINUE"
  echo "brief=$BRIEF ($(wc -l < "$BRIEF" | tr -d ' ') lines)"
  echo "started=$STARTED"
  echo "--------------------------------------------------------------------"
} | tee -a "$TRANSCRIPT"

# Run agy from within the workspace so relative paths resolve there.
set +e
( cd "$DIR" && agy "${AGY_ARGS[@]}" ) >"$RESULT_JSON" 2>>"$TRANSCRIPT"
AGY_EXIT=$?
set -e

{
  echo "--------------------------------------------------------------------"
  echo "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)  exit=$AGY_EXIT"
  echo "===================================================================="
} | tee -a "$TRANSCRIPT"

# Best-effort extraction of conversation id + final text from the JSON envelope.
# agy's exact schema may evolve; try several likely field names and never fail.
CONV_ID=""
if command -v jq >/dev/null 2>&1 && [ -s "$RESULT_JSON" ]; then
  CONV_ID=$(jq -r '
    (.conversation_id // .conversationId // .session_id // .sessionId
     // .conversation.id // .id // empty)' "$RESULT_JSON" 2>/dev/null | head -1 || true)
  jq -r '
    (.result // .response // .final_message // .message // .text // .output // empty)' \
    "$RESULT_JSON" 2>/dev/null > "$RESULT_TEXT" || true
fi
# Fallback: keep the raw JSON as the "text" if extraction produced nothing.
[ -s "$RESULT_TEXT" ] || cp "$RESULT_JSON" "$RESULT_TEXT" 2>/dev/null || true
# Persist conversation id for auto-resume on the next iteration.
[ -n "$CONV_ID" ] && printf '%s' "$CONV_ID" > "$CONV_FILE"

# Mirror the extracted text into the transcript for a readable audit trail.
{
  echo "----- agy final message (iter $ITER) -----"
  cat "$RESULT_TEXT" 2>/dev/null || true
  echo ""
} >> "$TRANSCRIPT"

# Append one durable record per delegation to delegations.jsonl — the dashboard reads
# this to show each agy sub-session (which model ran, its result, exit, duration). One
# line per iteration; append-only so the review→fix loop leaves a full history.
FINISHED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
case "$AGY_EXIT" in 0) STATUS="done";; 124) STATUS="timeout";; *) STATUS="failed";; esac
DELEG="$RUN_DIR/delegations.jsonl"
[ -f "$RESULT_TEXT" ] || : > "$RESULT_TEXT"
if command -v jq >/dev/null 2>&1; then
  jq -cn --arg iteration "$ITER" --arg model "$MODEL" --arg effort "$EFFORT" \
         --argjson exit "$AGY_EXIT" --arg status "$STATUS" \
         --arg started "$STARTED" --arg finished "$FINISHED" \
         --arg conversation "$CONV_ID" --arg result_path "$RESULT_TEXT" \
         --rawfile result "$RESULT_TEXT" \
     '{iteration:$iteration,model:$model,effort:$effort,exit:$exit,status:$status,
       started:$started,finished:$finished,conversation:$conversation,
       result_path:$result_path,result:($result|gsub("^\\s+|\\s+$";"")|.[0:280])}' \
     >> "$DELEG" 2>/dev/null || true
else
  printf '{"kind":"agy","iteration":"%s","model":"%s","status":"%s","exit":%d,"started":"%s","finished":"%s"}\n' \
    "$(json_str "$ITER")" "$(json_str "$MODEL")" "$STATUS" "$AGY_EXIT" "$STARTED" "$FINISHED" >> "$DELEG" || true
fi

echo "AGY_EXIT=$AGY_EXIT"
echo "AGY_RESULT_JSON=$RESULT_JSON"
echo "AGY_TRANSCRIPT=$TRANSCRIPT"
echo "AGY_CONVERSATION=${CONV_ID}"
echo "AGY_RESULT_TEXT=$RESULT_TEXT"

# Propagate a meaningful exit code: 0 success, 124 timeout, else agy's code.
exit "$AGY_EXIT"
