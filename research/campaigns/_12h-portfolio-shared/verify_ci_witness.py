"""Verify a CI refutation witness against the staged code document.

Determines the side (X or Z): a witness vector v is an X-logical iff
H_Z @ v = 0 and v is not in rowspace(H_X); a Z-logical iff H_X @ v = 0
and v is not in rowspace(H_Z). Prints the verdict as JSON.
"""
import json
import sys

import numpy as np

sys.path.insert(0, "verify")
import gf2  # noqa: E402


def dense(rows, n):
    m = np.zeros((len(rows), n), dtype=np.uint8)
    for i, r in enumerate(rows):
        for q in r:
            m[i, int(q)] = 1
    return m


def main():
    doc_path, wit_path = sys.argv[1], sys.argv[2]
    with open(doc_path, encoding="utf-8") as f:
        doc = json.load(f)
    with open(wit_path, encoding="utf-8") as f:
        wit = json.load(f)
    n = doc["n"]
    sup = wit["support"]
    assert len(sup) == wit["weight"], "weight mismatch"
    v = np.zeros(n, dtype=np.uint8)
    v[sup] = 1
    hx = dense(doc["checks"]["X"], n)
    hz = dense(doc["checks"]["Z"], n)
    out = {"slug": doc_path, "weight": len(sup)}
    if not (hx @ v % 2).any():
        # candidate Z-logical: commutes with X checks; not in rowspace(H_Z)?
        rk, piv = gf2.rref(hz)
        red = gf2.rref(np.vstack([hz, v]))[0]
        in_rowspace = (red[: rk.shape[0]].tolist() == rk.tolist()
                       if red.shape[0] >= rk.shape[0] else False)
        out["side"] = "Z"
        out["commutes_with_HX"] = True
        out["in_rowspace_HZ"] = bool(in_rowspace)
        out["is_logical"] = not in_rowspace
    elif not (hz @ v % 2).any():
        rk = gf2.rref(hx)[0]
        red = gf2.rref(np.vstack([hx, v]))[0]
        in_rowspace = (red[: rk.shape[0]].tolist() == rk.tolist()
                       if red.shape[0] >= rk.shape[0] else False)
        out["side"] = "X"
        out["commutes_with_HZ"] = True
        out["in_rowspace_HX"] = bool(in_rowspace)
        out["is_logical"] = not in_rowspace
    else:
        out["side"] = None
        out["is_logical"] = False
        out["error"] = "commutes with neither HX nor HZ"
    print(json.dumps(out, indent=1))
    return 0 if out.get("is_logical") else 1


if __name__ == "__main__":
    sys.exit(main())
