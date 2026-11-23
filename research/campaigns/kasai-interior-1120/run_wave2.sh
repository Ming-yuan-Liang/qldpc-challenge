#!/bin/bash
# Wave-2: 200k fast rungs (4-6) for the surviving q19 candidates.
DOCS2=(684-18-124 684-16-127)
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
for w in 0 1 2; do : > $W/w2_$w.txt; done
i=0
for doc in "${DOCS2[@]}"; do
  for r in 4 5 6; do
    if [ ! -f "$DIR/$doc-rung$r.json" ]; then
      echo "$DIR/$doc.json $r 200000 fast" >> $W/w2_$((i % 3)).txt
      i=$((i + 1))
    fi
  done
done
for w in 0 1 2; do
  (
    while read -r args; do
      echo "[$(date +%H:%M:%S)] START $args" >> $W/log.txt
      $PY -I research/campaigns/_12h-portfolio-shared/ladder_rerun.py $args \
        >> $W/log.txt 2>&1 \
        || echo "FAIL $args" >> $W/log.txt
    done < $W/w2_$w.txt
    echo "[$(date +%H:%M:%S)] wave2-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE2 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
