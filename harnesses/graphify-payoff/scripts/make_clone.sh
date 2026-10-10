#!/bin/sh
# Make an isolated clone of one base commit and set it up for one arm (plan.md Phase 2, Isolation).
#   sh local/graphify-eval/make_clone.sh <base-sha> <G|N|D> <new-dir>
# The clone holds only the base commit's history, has no remote and no later refs. Arm N removes the
# hook, the CLAUDE.md graphify section, .claude/CLAUDE.md and the project skill; arm D keeps the graph
# and the CLI but replaces the mandate with one line; arm G is the repository as it was.
# Graph builds run with every model API key unset so `graphify update` cannot call a model.
set -eu
base=$1; arm=$2; dir=$3
here=$(cd "$(dirname "$0")" && pwd)
cfg() { python3 -I "$here/config.py" get "$1"; }
main=$(cfg repo); heading=$(cfg instructions_section_heading); ifile=$(cfg instructions_file); gout=$(cfg graph_out)
[ -e "$dir" ] && { echo "refusing: $dir exists" >&2; exit 2; }
full=$(git -C "$main" rev-parse --verify "$base^{commit}") || exit 2
mkdir -p "$dir"
git -C "$dir" init -q
git -C "$dir" fetch -q "$main" "$full" || { echo "fetch of $full failed" >&2; exit 3; }
git -C "$dir" checkout -q --detach FETCH_HEAD
git -C "$dir" remote | grep -q . && { echo "clone has a remote" >&2; exit 3; }

strip_mandate() {  # keep everything before the graph section; append the note for arm D if asked
  python3 -I - "$dir/$ifile" "$1" "$heading" <<'EOF'
import re, sys
path, note, heading = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path).read()
head, sep, _ = text.partition('\n' + heading + '\n')
assert sep, 'no graph section at this commit'
open(path, 'w').write(head.rstrip('\n') + '\n' + (note + '\n' if note else ''))
EOF
}

case "$arm" in
  G) ;;
  N)
    strip_mandate ""
    cfg arm_N_remove | while read -r rel; do [ -n "$rel" ] && rm -rf "${dir:?}/$rel"; done
    python3 -I - "$dir/.claude/settings.json" <<'EOF'
import json, sys
p = sys.argv[1]; s = json.load(open(p))
s.get('hooks', {}).pop('PreToolUse', None)
json.dump(s, open(p, 'w'), indent=2)
EOF
    ;;
  D)
    strip_mandate "$(cfg arm_D_note)"
    python3 -I - "$dir/.claude/settings.json" <<'EOF'
import json, sys
p = sys.argv[1]; s = json.load(open(p))
s.get('hooks', {}).pop('PreToolUse', None)
json.dump(s, open(p, 'w'), indent=2)
EOF
    ;;
  *) echo "arm must be G, N or D" >&2; exit 2 ;;
esac

if [ "$arm" != N ]; then
  start=$(date +%s)
  ( cd "$dir" && env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u GEMINI_API_KEY -u GOOGLE_API_KEY -u OPENROUTER_API_KEY \
      -u GRAPHIFY_OUT GRAPHIFY_BACKEND=none graphify update "$(cfg code_root)" ) > "$dir/.graph-build.log" 2>&1 || true
  echo "graph build: $(( $(date +%s) - start ))s, $(wc -c < "$dir/.graph-build.log") bytes of output"
  [ "$gout" = graphify-out ] || ln -s "$gout" "$dir/graphify-out"
fi
echo "clone ready: $dir ($arm at $base)"
