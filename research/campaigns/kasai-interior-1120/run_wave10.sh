#!/bin/bash
# Wave-10: phantom filter - 3x20k numpy rungs for the batch-3 picks.
DOCS=(684-20-124 684-18-122 684-16-125)
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
for w in 0 1 2 3; do : > $W/w10_$w.txt; done
i=0
for doc in "${DOCS[@]}"; do
  for r in 1 2 3; do
    if [ ! -f "$DIR/$doc-rung$r.json" ]; then
      echo "$DIR/$doc.json $r 20000" >> $W/w10_$((i % 4)).txt
      i=$((i + 1))
    fi
  done
done
for w in 0 1 2 3; do
  (
    while read -r args; do
      echo "[$(date +%H:%M:%S)] START $args" >> $W/log.txt
      $PY -I research/campaigns/_12h-portfolio-shared/ladder_rerun.py $args \
        >> $W/log.txt 2>&1 \
        || echo "FAIL $args" >> $W/log.txt
    done < $W/w10_$w.txt
    echo "[$(date +%H:%M:%S)] wave10-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE10 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
