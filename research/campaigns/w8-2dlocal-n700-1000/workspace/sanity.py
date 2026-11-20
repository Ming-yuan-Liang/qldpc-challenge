import os, sys, time
import numpy as np

ROOT = r"C:\Users\Frieren\Desktop\qldpc\qldpc-challenge"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "research", "local2d"))
sys.path.insert(0, os.path.join(ROOT, "research", "kit"))
sys.path.insert(0, os.path.join(ROOT, "verify"))

# 1) gf2_fast loads?
try:
    import gf2_fast
    print("gf2_fast: OK", [a for a in dir(gf2_fast) if not a.startswith('_')])
except Exception as e:
    print("gf2_fast FAIL:", e)
    raise SystemExit(1)

# 2) surrogate fast backend wiring
import surrogate
res = surrogate.distance_rand_witness(HX=np.eye(4, dtype=np.int8)[:, :0].reshape(0,0) if False else None, HZ=None, trials=0) if False else None

# small real test: build 6x6 flagship, distance via fast
import boundary_engine as be
Sf = [(1, 0), (2, 0), (0, 2)]
Sg = [(0, 0), (2, 1), (2, 2)]
t0 = time.time()
HX, HZ, info = be.build_planar(6, 6, Sf, Sg)
t1 = time.time()
from css import verify_css
k = be.compute_k(HX, HZ)
print(f"6x6 flagship: n={HX.shape[1]} k={k} CSS={verify_css(HX,HZ)} build={t1-t0:.2f}s")

w = surrogate.distance_rand(HX, HZ, trials=2000, seed=3, backend="fast", threads=2, pair_depth=10)
print(f"fast d_rand 6x6 flagship: {w} (expect <=4)")

# 3) reproduce board entries at 20x20
for tag, sf, sg, want in [
    ("TILE4_MAIN", be.S_F_TILE4, be.S_G_TILE4_MAIN, (800, 18, 27)),
    ("B5-29", [[0,0],[1,3],[2,1],[4,4]], [[0,2],[1,4],[3,1],[4,0]], (800, 29, 24)),
    ("B5-32", [[0,0],[1,3],[4,0],[4,4]], [[0,4],[2,1],[3,2],[4,0]], (800, 32, 22)),
]:
    sf = [tuple(p) for p in sf]; sg = [tuple(p) for p in sg]
    t0 = time.time()
    HX, HZ, info = be.build_planar(20, 20, sf, sg)
    t1 = time.time()
    k = be.compute_k(HX, HZ)
    wx = int(be.reduce_weights(HX).sum(axis=1).max())
    wz = int(be.reduce_weights(HZ).sum(axis=1).max())
    print(f"{tag}: n={HX.shape[1]} k={k} w=({wx},{wz}) want={want} build={t1-t0:.1f}s info_promoted={info['n_promoted']} removed={info.get('n_removed_qubits')}")
