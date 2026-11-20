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
print("n=", HX.shape[1], "k=", be.compute_k(HX, HZ), flush=True)

for trials, pd in [(500, 10), (2000, 10), (5000, 22)]:
    t0 = time.time()
    w = surrogate.distance_rand(HX, HZ, trials=trials, seed=101,
                                backend="fast", threads=2, pair_depth=pd)
    t1 = time.time()
    print(f"fast trials={trials} pd={pd}: d_rand={w}  {t1-t0:.1f}s", flush=True)

t0 = time.time()
w = surrogate.distance_rand(HX, HZ, trials=2000, seed=101, pair_depth=10)
print(f"numpy trials=2000 pd=10: d_rand={w}  {time.time()-t0:.1f}s", flush=True)
