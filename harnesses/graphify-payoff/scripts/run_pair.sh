#!/bin/sh
# Run one Phase 2 orientation session per arm, sequentially, in prepared clones (plan.md Phase 2).
#   sh local/graphify-eval/run_pair.sh <milestone> <runs-dir> <arm> [<arm> ...]
# Each clone must already exist at <runs-dir>/clone-<arm> (make_clone.sh + check_clone.sh). The arm
# order given is the order run; the caller randomises it and this script records it. Each run gets
# its own session id so its transcript can be found, a dollar cap, no subagents, and no permission
# prompts (the clone is isolated: no remote, base-commit history only).
set -u
milestone=$1; runs=$2; shift 2
here=$(cd "$(dirname "$0")" && pwd)
cfg() { python3 -I "$here/config.py" get "$1"; }
model=${RUN_MODEL:-$(cfg model)}
cap_usd=${RUN_CAP_USD:-$(cfg cap_usd)}
prompt=$(cfg prompt | sed "s/{task}/$milestone/g")
log=$runs/runs.jsonl
for arm in "$@"; do
  dir=$runs/clone-$arm
  sid=$(python3 -I -c 'import uuid;print(uuid.uuid4())')
  start=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  ( cd "$dir" && claude -p "$prompt" --model "$model" --session-id "$sid" --max-budget-usd "$cap_usd" \
      --dangerously-skip-permissions --disallowedTools Agent Task --output-format json \
      > "$runs/result-$arm.json" 2> "$runs/stderr-$arm.txt" )
  code=$?
  end=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  plan=$([ -f "$dir/PLAN.md" ] && echo true || echo false)
  [ "$plan" = true ] && cp "$dir/PLAN.md" "$runs/PLAN-$arm.md"  # survives the clone's removal
  python3 -I - "$log" "$arm" "$sid" "$start" "$end" "$code" "$plan" "$dir" "$runs/result-$arm.json" "$model" <<'EOF'
import json, sys
log, arm, sid, start, end, code, plan, d, res = sys.argv[1:10]
row = {'arm': arm, 'session_id': sid, 'start': start, 'end': end, 'exit': int(code), 'plan_written': plan == 'true',
       'clone': d, 'model': sys.argv[10] if len(sys.argv) > 10 else None}
try:
    r = json.load(open(res))
    row.update({'cost_usd': r.get('total_cost_usd'), 'turns': r.get('num_turns'), 'duration_ms': r.get('duration_ms'),
                'is_error': r.get('is_error'), 'subtype': r.get('subtype')})
except Exception as e:  # noqa: BLE001
    row['result_parse_error'] = str(e)
open(log, 'a').write(json.dumps(row) + '\n')
print(json.dumps(row))
EOF
done
