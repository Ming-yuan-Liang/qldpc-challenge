#!/bin/bash
# Wave-30: 544-16-94 deep ladder stage 2 (2M x2, fast pd12, 2 workers).
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
JOBS=("$DIR/544-16-94.json 7 2000000 fast 12" \
      "$DIR/544-16-94.json 8 2000000 fast 12")
for w in 0 1; do : > $W/w30_$w.txt; done
i=0
for job in "${JOBS[@]}"; do
  doc=$(echo "$job" | awk '{print $1}')
  r=$(echo "$job" | awk '{print $2}')
  rungf="${doc%.json}-rung$r.json"
  if [ ! -f "$rungf" ]; then
    echo "$job" >> $W/w30_$((i % 2)).txt
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
    done < $W/w30_$w.txt
    echo "[$(date +%H:%M:%S)] wave30-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE30 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
