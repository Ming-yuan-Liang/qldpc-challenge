#!/bin/bash
# Wave-32: 121 convergence probes (8M pd12 x2) + 120 8M finals (pd10 x2).
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
JOBS=("$DIR/684-20-121.json 11 8000000 fast 12" \
      "$DIR/684-20-121.json 12 8000000 fast 12" \
      "$DIR/684-20-120.json 9 8000000 fast 10" \
      "$DIR/684-20-120.json 10 8000000 fast 10")
for w in 0 1 2 3; do : > $W/w32_$w.txt; done
i=0
for job in "${JOBS[@]}"; do
  doc=$(echo "$job" | awk '{print $1}')
  r=$(echo "$job" | awk '{print $2}')
  rungf="${doc%.json}-rung$r.json"
  if [ ! -f "$rungf" ]; then
    echo "$job" >> $W/w32_$((i % 4)).txt
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
    done < $W/w32_$w.txt
    echo "[$(date +%H:%M:%S)] wave32-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE32 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
