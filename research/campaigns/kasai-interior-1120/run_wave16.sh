#!/bin/bash
# Wave-16: 684-16-126 deep ladder final (8M x2, fast pd10 - CI resolution).
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
JOBS=("$DIR/684-16-126.json 9 8000000 fast 10" \
      "$DIR/684-16-126.json 10 8000000 fast 10")
for w in 0 1; do : > $W/w16_$w.txt; done
i=0
for job in "${JOBS[@]}"; do
  doc=$(echo "$job" | awk '{print $1}')
  r=$(echo "$job" | awk '{print $2}')
  rungf="${doc%.json}-rung$r.json"
  if [ ! -f "$rungf" ]; then
    echo "$job" >> $W/w16_$((i % 2)).txt
    i=$((i + 1))
  fi
done
for w in 0 1; do
  (
    while read -r args; do
      echo "[$(date +%H:%M:%S)] START $args" >> $W/log.txt
      $PY -I research/campaigns/_12h-portfolio-shared/ladder_rerun.py $args \
        >> $W/log.txt 2>&1 \
        || echo "FAIL $args" >> $W/log.txt
    done < $W/w16_$w.txt
    echo "[$(date +%H:%M:%S)] wave16-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE16 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
