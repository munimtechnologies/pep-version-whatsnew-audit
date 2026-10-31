"""Audit of PEP Python-Version headers against CPython's What's New pages.

MV2, Munim, Inc. Apache-2.0. Made with AI agents.

Pure functions only (no network); job.py downloads the snapshot and calls analyze().
"""
import re

VERSION_RE = re.compile(r"(\d+)\.(\d+)")
# :pep:`695`, :pep:`the PEG parser <617>`, :pep:`guide <0632#migration-advice>`
ROLE_RE = re.compile(r":pep:`(?:[^`<]*<)?\s*0*(\d+)")
# PEP 695, PEPs 484
PLAIN_RE = re.compile(r"\bPEPs?\s+0*(\d+)\b")
# an RST section underline: one punctuation character repeated, nothing else
UNDERLINE_RE = re.compile(r"""^([=\-~^*#"+`'])\1{2,}\s*$""")

# Pre-registered bars (PREREG.md); do not change after the data run.
P1_BAR = 0.90
P2_BAR = 0.50
P3_BAR = 0.80
P4_MIN = 3
P4_LAST = (3, 14)
ACTIVE_OK = ("Final", "Accepted", "Provisional")
INACTIVE = ("Draft", "Deferred", "Rejected", "Withdrawn")


def parse_versions(value):
    """'2.6, 3.0' -> [(2, 6), (3, 0)]; None or '2.x' -> []."""
    if not value:
        return []
    return sorted({(int(a), int(b)) for a, b in VERSION_RE.findall(str(value))})


def vstr(v):
    return "%d.%d" % v if v else None


def pep_refs(text):
    """Every PEP number referenced in a piece of RST text."""
    return ({int(n) for n in ROLE_RE.findall(text)}
            | {int(n) for n in PLAIN_RE.findall(text)})


def heading_lines(text):
    """Section titles: an unindented text line directly above an underline."""
    lines = text.splitlines()
    out = []
    for i in range(len(lines) - 1):
        line = lines[i]
        if not line.strip() or line[0] in " \t" or UNDERLINE_RE.match(line):
            continue
        if UNDERLINE_RE.match(lines[i + 1]):
            out.append(line.strip())
    return out


def index_whatsnew(whatsnew):
    """{'3.12': rst text} -> {(3, 12): {'all': {pep, ...}, 'heads': {pep, ...}}}."""
    idx = {}
    for name, text in whatsnew.items():
        vs = parse_versions(name)
        if len(vs) != 1:
            continue
        heads = set()
        for h in heading_lines(text):
            heads |= pep_refs(h)
        idx[vs[0]] = {"all": pep_refs(text), "heads": heads}
    return idx


def share(k, n):
    return k / n if n else None


def verdict(ok):
    return "HELD" if ok else "FAILED"


def row_out(r):
    out = dict(r)
    for k in ("header", "mentions", "heads"):
        out[k] = [vstr(v) for v in r[k]]
    out["first_py3_head"] = vstr(r["first_py3_head"])
    out["first_py3_mention"] = vstr(r["first_py3_mention"])
    return out


def build_rows(peps, idx):
    versions = sorted(idx)
    rows = []
    for key in sorted(peps, key=lambda k: int(k)):
        e = peps[key]
        n = int(e.get("number", key))
        header = parse_versions(e.get("python_version"))
        mentions = [v for v in versions if n in idx[v]["all"]]
        heads = [v for v in versions if n in idx[v]["heads"]]
        py3_heads = [v for v in heads if v[0] == 3]
        py3_mentions = [v for v in mentions if v[0] == 3]
        rows.append({
            "number": n,
            "title": e.get("title"),
            "status": e.get("status"),
            "type": e.get("type"),
            "topic": e.get("topic") or "",
            "python_version": e.get("python_version"),
            "header": header,
            "mentions": mentions,
            "heads": heads,
            "first_py3_head": py3_heads[0] if py3_heads else None,
            "first_py3_mention": py3_mentions[0] if py3_mentions else None,
        })
    return rows


def analyze(peps, whatsnew):
    idx = index_whatsnew(whatsnew)
    rows = build_rows(peps, idx)
    std = [r for r in rows if r["type"] == "Standards Track"]
    single3 = [r for r in std if len(r["header"]) == 1 and r["header"][0][0] == 3]
    final3 = [r for r in single3 if r["status"] == "Final"]

    # P1a: header vs the first 3.x What's New that has the PEP in a section title
    s1a = [r for r in final3 if r["first_py3_head"]]
    mism_a = [r for r in s1a if r["header"][0] != r["first_py3_head"]]
    p1a = share(len(s1a) - len(mism_a), len(s1a))

    # P1b: header vs the first 3.x What's New that mentions the PEP anywhere
    s1b = [r for r in final3 if r["first_py3_mention"]]
    mism_b = [r for r in s1b if r["header"][0] != r["first_py3_mention"]]
    p1b = share(len(s1b) - len(mism_b), len(s1b))

    # P2: among P1b mismatches, the header names an earlier release (a slip)
    earlier = [r for r in mism_b if r["header"][0] < r["first_py3_mention"]]
    p2 = share(len(earlier), len(mism_b))

    # P3: the What's New for the header's own version mentions the PEP
    s3 = [r for r in final3 if r["header"][0] in idx]
    s3_hit = [r for r in s3 if r["header"][0] in r["mentions"]]
    p3 = share(len(s3_hit), len(s3))

    # P4: still Accepted, header <= 3.14, and that release's What's New mentions it
    p4 = [r for r in single3 if r["status"] == "Accepted"
          and r["header"][0] <= P4_LAST and r["header"][0] in r["mentions"]]

    missing_header = [r for r in std if not r["header"] and r["status"] in ACTIVE_OK
                      and any(v[0] == 3 for v in r["heads"])
                      and "packaging" not in r["topic"]]
    headlined_inactive = [r for r in rows if r["heads"] and r["status"] in INACTIVE]
    multi = [r for r in std if len(r["header"]) > 1]
    single2 = [r for r in std if len(r["header"]) == 1 and r["header"][0][0] == 2
               and r["status"] == "Final"]
    s2 = [r for r in single2 if any(v[0] == 2 for v in r["heads"])]
    s2_match = [r for r in s2
                if r["header"][0] == [v for v in r["heads"] if v[0] == 2][0]]
    header_headlined = [r for r in s1a if r["header"][0] in r["heads"]]

    status_hist = {}
    for r in rows:
        status_hist[r["status"]] = status_hist.get(r["status"], 0) + 1

    return {
        "n_peps": len(rows),
        "whatsnew_versions": [vstr(v) for v in sorted(idx)],
        "status_hist": status_hist,
        "n_standards_track": len(std),
        "n_single_3x_header": len(single3),
        "n_final_single_3x": len(final3),
        "P1a": {"n": len(s1a), "match": len(s1a) - len(mism_a), "share": p1a,
                "bar": P1_BAR, "verdict": verdict(p1a is not None and p1a >= P1_BAR),
                "mismatches": [row_out(r) for r in mism_a]},
        "P1b": {"n": len(s1b), "match": len(s1b) - len(mism_b), "share": p1b,
                "bar": P1_BAR, "verdict": verdict(p1b is not None and p1b >= P1_BAR),
                "mismatches": [row_out(r) for r in mism_b]},
        "P2": {"n": len(mism_b), "header_earlier": len(earlier), "share": p2,
               "bar": P2_BAR,
               "verdict": "NOT TESTABLE" if not mism_b else verdict(p2 > P2_BAR)},
        "P3": {"n": len(s3), "hit": len(s3_hit), "share": p3, "bar": P3_BAR,
               "verdict": "NOT TESTABLE" if not s3 else verdict(p3 >= P3_BAR),
               "misses": [row_out(r) for r in s3 if r not in s3_hit]},
        "P4": {"count": len(p4), "min": P4_MIN, "last_version": vstr(P4_LAST),
               "verdict": verdict(len(p4) >= P4_MIN),
               "peps": [row_out(r) for r in p4]},
        "descriptive": {
            "missing_header_headlined": [row_out(r) for r in missing_header],
            "headlined_inactive": [row_out(r) for r in headlined_inactive],
            "multi_version_headers": len(multi),
            "header_headlined_anywhere_share": share(len(header_headlined), len(s1a)),
            "py2_line": {"n": len(s2), "match": len(s2_match)},
        },
        "rows": [row_out(r) for r in rows],
    }
