#!/bin/sh
# Phase 2 batch: for each milestone and repetition, build fresh G and N clones, verify them, and run
# the pair in a coin-flipped order (plan.md section 8, Phase 2, as changed on 2026-10-10).
#   RUN_MODEL=claude-opus-5-5 RUN_CAP_USD=4 sh local/graphify-eval/run_batch.sh <runs-dir> <reps>
set -u
runs=$1; reps=$2
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$runs"
{ echo "claude: $(claude --version 2>&1)"; echo "graphify: $(graphify --version 2>&1)"
  echo "model: ${RUN_MODEL:-$(python3 -I "$here/config.py" get model)} cap: ${RUN_CAP_USD:-$(python3 -I "$here/config.py" get cap_usd)}"; date -u; } > "$runs/batch-info.txt"
python3 -I "$here/config.py" get tasks | while read -r ms base tick; do
  rep=1
  while [ "$rep" -le "$reps" ]; do
    d=$runs/$ms/rep$rep; mkdir -p "$d"
    order=$(python3 -I -c "import random;print(random.choice(['G N','N G']))")
    echo "$order" > "$d/order.txt"
    ok=1
    for arm in G N; do
      sh "$here/make_clone.sh" "$base" "$arm" "$d/clone-$arm" > "$d/make-$arm.txt" 2>&1 || ok=0
      sh "$here/check_clone.sh" "$base" "$arm" "$d/clone-$arm" > "$d/check-$arm.txt" 2>&1 || ok=0
    done
    if [ "$ok" = 1 ]; then
      set -- $order
      sh "$here/run_pair.sh" "$ms" "$d" "$@" >> "$runs/batch.log" 2>&1
    else
      echo "{\"milestone\": \"$ms\", \"rep\": $rep, \"skipped\": \"clone check failed\"}" >> "$runs/batch.log"
    fi
    echo "$ms rep$rep done $(date -u +%H:%M:%S)" >> "$runs/batch.log"
    rep=$((rep + 1))
  done
done
echo "batch finished $(date -u)" >> "$runs/batch.log"
