#!/bin/bash
# Wave-33: batch-7 ghost filter (3 heads x 20k numpy rungs 1-3, 2 workers).
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
JOBS=("$DIR/684-16-126b.json 1 20000 numpy 10" \
      "$DIR/684-16-126b.json 2 20000 numpy 10" \
      "$DIR/684-16-126b.json 3 20000 numpy 10" \
      "$DIR/544-20-92.json 1 20000 numpy 10" \
      "$DIR/544-20-92.json 2 20000 numpy 10" \
      "$DIR/544-20-92.json 3 20000 numpy 10" \
      "$DIR/544-14-96.json 1 20000 numpy 10" \
      "$DIR/544-14-96.json 2 20000 numpy 10" \
      "$DIR/544-14-96.json 3 20000 numpy 10")
for w in 0 1; do : > $W/w33_$w.txt; done
i=0
for job in "${JOBS[@]}"; do
  doc=$(echo "$job" | awk '{print $1}')
  r=$(echo "$job" | awk '{print $2}')
  rungf="${doc%.json}-rung$r.json"
  if [ ! -f "$rungf" ]; then
    echo "$job" >> $W/w33_$((i % 2)).txt
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
    done < $W/w33_$w.txt
    echo "[$(date +%H:%M:%S)] wave33-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE33 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
