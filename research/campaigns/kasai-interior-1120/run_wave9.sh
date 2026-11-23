#!/bin/bash
# Wave-9: 2M pd32 rungs (39-42) for 684-18-124 - deep-pair convergence.
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
for w in 0 1 2 3; do : > $W/w9_$w.txt; done
i=0
for r in 39 40 41 42; do
  if [ ! -f "$DIR/684-18-124-rung$r.json" ]; then
    echo "$DIR/684-18-124.json $r 2000000 fast 32" >> $W/w9_$((i % 4)).txt
    i=$((i + 1))
  fi
done
for w in 0 1 2 3; do
  (
    while read -r args; do
      echo "[$(date +%H:%M:%S)] START $args" >> $W/log.txt
      $PY -I research/campaigns/_12h-portfolio-shared/ladder_rerun.py $args \
        >> $W/log.txt 2>&1 \
        || echo "FAIL $args" >> $W/log.txt
    done < $W/w9_$w.txt
    echo "[$(date +%H:%M:%S)] wave9-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE9 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
