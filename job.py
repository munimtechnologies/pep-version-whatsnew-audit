"""Data run: snapshot peps.json and CPython's Doc/whatsnew, then grade PREREG.md.

MV2, Munim, Inc. Apache-2.0. Made with AI agents.
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit  # noqa: E402

UA = {"User-Agent": "mv2-pep-version-audit/0.1 (Munim, Inc.; mv2@munimtech.com)"}
PEPS_URL = "https://peps.python.org/api/peps.json"
COMMIT_URL = "https://api.github.com/repos/python/cpython/commits/main"
RAW = "https://raw.githubusercontent.com/python/cpython/{ref}/Doc/whatsnew/{v}.rst"
CANDIDATES = ["2.%d" % i for i in range(8)] + ["3.%d" % i for i in range(21)]


def get(url, tries=3):
    err = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            err = e
        except Exception as e:  # network hiccup: retry
            err = e
        time.sleep(2 * (k + 1))
    raise err


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    snap = os.path.join(a.out_dir, "snapshot")
    os.makedirs(os.path.join(snap, "whatsnew"), exist_ok=True)

    fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    peps_raw = get(PEPS_URL)
    with open(os.path.join(snap, "peps.json"), "wb") as f:
        f.write(peps_raw)

    try:
        ref = json.loads(get(COMMIT_URL))["sha"]
    except Exception as e:  # rate limit: fall back to the branch name, say so
        print("commit lookup failed (%r); using main" % (e,))
        ref = "main"

    whatsnew, hashes = {}, {}
    for v in CANDIDATES:
        b = get(RAW.format(ref=ref, v=v))
        if b is None:
            continue
        whatsnew[v] = b.decode("utf-8")
        hashes[v] = sha256(b)
        with open(os.path.join(snap, "whatsnew", v + ".rst"), "wb") as f:
            f.write(b)

    res = audit.analyze(json.loads(peps_raw), whatsnew)
    res["source"] = {
        "fetched_at": fetched_at,
        "peps_json_url": PEPS_URL,
        "peps_json_sha256": sha256(peps_raw),
        "cpython_ref": ref,
        "whatsnew_sha256": hashes,
    }
    rows = res.pop("rows")
    with open(os.path.join(a.out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    with open(os.path.join(a.out_dir, "peps.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
    cols = ["number", "status", "type", "topic", "python_version", "header",
            "first_py3_head", "first_py3_mention", "heads", "mentions", "title"]
    with open(os.path.join(a.out_dir, "peps.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([";".join(r[c]) if isinstance(r[c], list) else r[c] for c in cols])
    for k in ("P1a", "P1b", "P2", "P3", "P4"):
        print(k, res[k]["verdict"], {x: res[k][x] for x in res[k]
                                     if x in ("n", "match", "share", "count", "hit")})


if __name__ == "__main__":
    main()
