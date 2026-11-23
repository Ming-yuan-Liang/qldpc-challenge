#!/bin/bash
# A1 batch-2 sweeps: sequential to leave CPU for the wave-1 ladders.
PY=.venv/Scripts/python.exe
LOG=research/campaigns/kasai-interior-1120/sweep_batch2.log
echo "[$(date +%H:%M:%S)] batch2 start" >> $LOG
$PY -I research/campaigns/kasai-interior-1120/interior_sweep.py \
  --q 19 --weight 8 --num 6000 --seed 42004 --workers 2 >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] q19 s42004 done" >> $LOG
$PY -I research/campaigns/kasai-interior-1120/interior_sweep.py \
  --q 17 --weight 8 --num 6000 --seed 42005 --workers 2 >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] q17 s42005 done -> BATCH2 ALL DONE" >> $LOG
