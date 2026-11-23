"""Fetch a GitHub Actions job log (redirect-safe). Usage: fetch_joblog.py <job_id> <out.txt>"""
import sys
import urllib.error
import urllib.request
from pathlib import Path

TOK = (Path(__file__).resolve().parents[3] / "research/candidates/.pat").read_text(encoding="utf-8").strip()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(job_id):
    url = f"https://api.github.com/repos/unitaryfoundation/qldpc-challenge/actions/jobs/{job_id}/logs"
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + TOK)
    req.add_header("User-Agent", "ci-supervision")
    opener = urllib.request.build_opener(NoRedirect)
    for hop in range(4):
        try:
            with opener.open(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                loc = e.headers["Location"]
                req = urllib.request.Request(loc)
                req.add_header("Authorization", "Bearer " + TOK)
                req.add_header("User-Agent", "ci-supervision")
                continue
            raise
    raise SystemExit("too many redirects")


if __name__ == "__main__":
    data = fetch(sys.argv[1])
    Path(sys.argv[2]).write_bytes(data)
    print("saved", sys.argv[2], len(data), "bytes")
