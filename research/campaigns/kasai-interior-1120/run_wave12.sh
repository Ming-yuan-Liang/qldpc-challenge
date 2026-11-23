#!/bin/bash
# Wave-12: 684-16-125 deep ladder (200k x3, 2M x2, 8M x2).
DIR=research/candidates/a1-kasai-1120
PY=.venv/Scripts/python.exe
W=research/campaigns/kasai-interior-1120/wave1
JOBS=("$DIR/684-16-125.json 4 200000 fast 12" \
      "$DIR/684-16-125.json 5 200000 fast 12" \
      "$DIR/684-16-125.json 6 200000 fast 12" \
      "$DIR/684-16-125.json 7 2000000 fast 12" \
      "$DIR/684-16-125.json 8 2000000 fast 12" \
      "$DIR/684-16-125.json 9 8000000 fast 10" \
      "$DIR/684-16-125.json 10 8000000 fast 10")
for w in 0 1 2 3; do : > $W/w12_$w.txt; done
i=0
for job in "${JOBS[@]}"; do
  r=$(echo "$job" | awk '{print $2}')
  if [ ! -f "$DIR/684-16-125-rung$r.json" ]; then
    echo "$job" >> $W/w12_$((i % 4)).txt
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
    done < $W/w12_$w.txt
    echo "[$(date +%H:%M:%S)] wave12-worker$w done" >> $W/log.txt
  ) &
done
wait
echo "WAVE12 ALL DONE $(date +%H:%M:%S)" >> $W/log.txt
