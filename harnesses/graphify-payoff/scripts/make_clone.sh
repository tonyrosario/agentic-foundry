#!/bin/sh
# Make an isolated clone of one base commit and set it up for one arm (plan.md Phase 2, Isolation).
#   sh local/graphify-eval/make_clone.sh <base-sha> <G|N|D> <new-dir>
# The clone holds only the base commit's history, has no remote and no later refs. Arm N removes the
# hook, the CLAUDE.md graphify section, .claude/CLAUDE.md and the project skill; arm D keeps the graph
# and the CLI but replaces the mandate with one line; arm G is the repository as it was, or, when the
# base commit no longer carries the hook and `arm_G_restore` is configured, the repository with the
# hook settings and the graph section re-installed from that commit.
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

restore_mandate() {  # arm G on a repo that dropped the mandate: take hook files and the section from the restore commit
  rc=$1; shift
  for rel in "$@"; do
    mkdir -p "$dir/$(dirname "$rel")"
    git -C "$main" show "$rc:$rel" > "$dir/$rel" || { echo "no $rel at $rc" >&2; exit 4; }
  done
  git -C "$main" show "$rc:$ifile" > "$dir/.restore-instructions.tmp"
  python3 -I - "$dir/$ifile" "$heading" "$dir/.restore-instructions.tmp" <<'EOF'
import os, sys
path, heading, tmp = sys.argv[1], sys.argv[2], sys.argv[3]
sep = '\n' + heading + '\n'
old = open(tmp).read()
os.remove(tmp)
i = old.find(sep)
assert i >= 0, 'no graph section at the restore commit'
rest = old[i + 1:]
j = rest.find('\n## ', 1)
section = rest if j < 0 else rest[:j]
text = open(path).read()
head, found, _ = text.partition(sep)
base = head if found else text
open(path, 'w').write(base.rstrip('\n') + '\n\n' + section.strip('\n') + '\n')
EOF
  echo "arm G: hook settings and the '$heading' section installed from $rc"
}

case "$arm" in
  G)
    rc=$(cfg arm_G_restore_commit)
    # shellcheck disable=SC2046  # file list is space-separated by design
    if [ -n "$rc" ] && ! grep -q "$(cfg hook_command_prefix)" "$dir/.claude/settings.json" 2>/dev/null; then
      restore_mandate "$rc" $(cfg arm_G_restore_files)
    fi
    ;;
  N)
    strip_mandate ""
    cfg arm_N_remove | while read -r rel; do [ -n "$rel" ] && rm -rf "${dir:?}/$rel"; done
    python3 -I - "$dir/$ifile" "$(cfg arm_N_edits)" <<'EOF'
import json, sys
path, edits = sys.argv[1], json.loads(sys.argv[2])
text = open(path).read()
for old, new in edits:
    if old in text:
        text = text.replace(old, new)
open(path, 'w').write(text)
EOF
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
