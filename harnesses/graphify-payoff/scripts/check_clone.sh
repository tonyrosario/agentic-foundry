#!/bin/sh
# Verify an arm clone before a run (plan.md Phase 0 step 5 and Phase 2 Isolation).
#   sh local/graphify-eval/check_clone.sh <base-sha> <G|N|D> <dir>
# Prints one PASS/FAIL line per check and exits non-zero on any FAIL.
set -u
base=$1; arm=$2; dir=$3; fail=0
here=$(cd "$(dirname "$0")" && pwd)
cfg() { python3 -I "$here/config.py" get "$1"; }
heading=$(cfg instructions_section_heading); ifile=$(cfg instructions_file); gout=$(cfg graph_out); hookcmd=$(cfg hook_command_prefix)
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; fail=1; }
full=$(git -C "$dir" rev-parse HEAD)
[ "$(git -C "$dir" rev-parse --short "$full")" = "$(git -C "$dir" rev-parse --short "$base")" ] \
  && ok "HEAD is $base" || bad "HEAD is not $base"
[ -z "$(git -C "$dir" remote)" ] && ok "no remote" || bad "remote configured"
[ "$(git -C "$dir" log --all --format=%H | head -1)" = "$full" ] && ok "no ref past the base" || bad "ref past the base"
[ "$(git -C "$dir" rev-list --all --count)" = "$(git -C "$dir" rev-list HEAD --count)" ] \
  && ok "all objects reachable only from the base" || bad "extra reachable commits"
[ -z "$(git -C "$dir" stash list)" ] && ok "no stash" || bad "stash present"
hook=$(python3 -I -c 'import json,sys,os;p=sys.argv[1];print(json.dumps(json.load(open(p)).get("hooks",{}).get("PreToolUse",[])) if os.path.exists(p) else "[]")' "$dir/.claude/settings.json")
case "$arm" in
  G) echo "$hook" | grep -qF "$hookcmd" && ok "hook present" || bad "hook missing";
     grep -qF "$heading" "$dir/$ifile" && ok "mandate present" || bad "mandate missing";
     [ -f "$dir/.claude/CLAUDE.md" ] && ok "skill pointer present" || bad "skill pointer missing" ;;
  N) echo "$hook" | grep -qF "$hookcmd" && bad "hook still present" || ok "hook removed";
     grep -q 'graphify' "$dir/$ifile" && bad "$ifile still mentions graphify" || ok "$ifile has no graphify";
     for rel in $(cfg arm_N_remove); do [ -e "$dir/$rel" ] && bad "$rel present" || ok "$rel removed"; done;
     [ -e "$dir/graphify-out" ] || [ -e "$dir/$gout" ] && bad "graph present" || ok "no graph" ;;
  D) echo "$hook" | grep -qF "$hookcmd" && bad "hook still present" || ok "hook removed";
     grep -q 'MANDATORY\|first run `graphify query' "$dir/$ifile" && bad "mandate present" || ok "mandate removed";
     grep -q 'graphify query' "$dir/$ifile" && ok "one-line note present" || bad "note missing";
     [ -f "$dir/.claude/CLAUDE.md" ] && ok "skill pointer kept (plan: D is G minus mandate and hook)" || bad "skill pointer missing" ;;
esac
if [ "$arm" != N ]; then
  [ -f "$dir/$gout/graph.json" ] && ok "graph built" || bad "graph missing"
  built=$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1])).get("built_at_commit",""))' "$dir/$gout/graph.json")
  [ "$built" = "$full" ] && ok "graph built_at_commit is the base" || bad "graph built at $built"
  # graphify prints a "Tip: set GEMINI_API_KEY" line when no key is set; that is the absence of a backend.
  grep -v '^Tip:' "$dir/.graph-build.log" | grep -qiE 'labell?ing|backend|using model|semantic extraction' \
    && bad "build log mentions a model backend (read $dir/.graph-build.log)" || ok "build log names no model backend"
  grep -q '^Tip: set GEMINI_API_KEY' "$dir/.graph-build.log" && ok "build ran without a model key" || bad "no 'no key' tip in build log"
  grep -q 'TRUNCATED\|Error\|Traceback' "$dir/.graph-build.log" && bad "build log has errors" || ok "build log clean"
fi
# The clone's Claude Code project folder (per-project memory) must not exist or must be empty.
slug=$(printf '%s' "$dir" | sed 's#[/._]#-#g')
mem="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/$slug/memory"
[ -z "$(ls -A "$mem" 2>/dev/null)" ] && ok "project memory empty ($mem)" || bad "project memory not empty: $mem"
exit $fail
