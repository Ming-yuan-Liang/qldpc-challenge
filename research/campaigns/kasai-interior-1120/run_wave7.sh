#!/bin/bash
# Wave-6: 2M fast rungs (23-26) for 684-18-124 only - convergence push.
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
for w in 0 1 2 3; do : > $W/w7_$w.txt; done
i=0
for r in 27 28 29 30 31 32 33 34; do
  if [ ! -f "$DIR/684-18-124-rung$r.json" ]; then
    echo "$DIR/684-18-124.json $r 2000000 fast" >> $W/w7_$((i % 4)).txt
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
    done < $W/w7_$w.txt
    echo "[$(date +%H:%M:%S)] wave6-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE7 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
