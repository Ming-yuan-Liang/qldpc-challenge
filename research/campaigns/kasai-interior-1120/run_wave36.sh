#!/bin/bash
# Wave-36: 684-16-126b deep ladder stage 1 (200k x3, fast pd12, 2 workers).
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
JOBS=("$DIR/684-16-126b.json 4 200000 fast 12" \
      "$DIR/684-16-126b.json 5 200000 fast 12" \
      "$DIR/684-16-126b.json 6 200000 fast 12")
for w in 0 1; do : > $W/w36_$w.txt; done
i=0
for job in "${JOBS[@]}"; do
  doc=$(echo "$job" | awk '{print $1}')
  r=$(echo "$job" | awk '{print $2}')
  rungf="${doc%.json}-rung$r.json"
  if [ ! -f "$rungf" ]; then
    echo "$job" >> $W/w36_$((i % 2)).txt
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
    done < $W/w36_$w.txt
    echo "[$(date +%H:%M:%S)] wave36-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE36 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
