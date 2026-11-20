import os, sys, time
import numpy as np
ROOT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "research", "local2d"))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))
import boundary_engine as be
import surrogate

sf = [tuple(p) for p in [[0,0],[1,3],[2,1],[4,4]]]
sg = [tuple(p) for p in [[0,2],[1,4],[3,1],[4,0]]]
HX, HZ, info = be.build_planar(20, 20, sf, sg)
print("n=", HX.shape[1], "k=", be.compute_k(HX, HZ))

for trials, pd in [(20000, 22), (100000, 20)]:
    t0 = time.time()
    w = surrogate.distance_rand(HX, HZ, trials=trials, seed=101,
                                backend="fast", threads=2, pair_depth=pd)
    t1 = time.time()
    print(f"fast trials={trials} pd={pd}: d_rand={w}  {t1-t0:.1f}s")

# numpy comparison at 20000 for the same code
t0 = time.time()
w = surrogate.distance_rand(HX, HZ, trials=20000, seed=101, pair_depth=22)
t1 = time.time()
print(f"numpy trials=20000 pd=22: d_rand={w}  {t1-t0:.1f}s")
