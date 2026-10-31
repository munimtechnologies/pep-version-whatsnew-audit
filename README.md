# pep-version-whatsnew-audit

Does each Python PEP's `Python-Version` header name the release its feature actually shipped in?
This audit checks every PEP in https://peps.python.org/api/peps.json against CPython's own
"What's New in Python X.Y" pages and lists each disagreement for a person to check.

By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Code Apache-2.0; text and results
CC BY 4.0.

## Result (v1.0.0, graded 2026-10-31)

- **The headers are right.** For Final Standards Track PEPs with one 3.x header, the header matched
  the first 3.x What's New that headlines the PEP in 100 of 102 cases (98.0%) and the first that
  mentions it in 182 of 186 (97.8%). Every disagreement was read by hand: **none is a confirmed
  header error** (two features shipped in stages, one was mentioned before it shipped, one was
  backported, one was a parser artefact, and PEP 3156 / asyncio is debatable).
- **Two predictions failed, and both are reported.** P2 (disagreements are mostly slipped features
  with stale headers) failed at 2 of 4, and none of the four is a slip. P4 (at least 3 shipped PEPs
  still marked Accepted) failed with 1: PEP 739, which already has an open "Mark as Final" PR.
- **The one real error is in What's New.** What's New in Python 3.12 credits the Unstable C API
  tier to **PEP 697** instead of **PEP 689**, in the release highlights and under C API changes.
  See FIXLIST.md for the evidence.

Details: GRADING.md. Numbers: `results/run1-summary.json`; one row per PEP: `results/peps.csv`.

## Status

- 2026-10-31: pre-registered (PREREG.md) before any data was downloaded. Five predictions, bars
  fixed in `audit.py`.
- 2026-10-31: data run finished (CPython main `683fca84`, peps.json SHA-256 `bb8fea4b...`); graded
  by hand (GRADING.md); fix list (FIXLIST.md).
- Follow-up: a mechanical check of every PEP number/title pair in CPython's `Doc/` tree is
  pre-registered in https://github.com/munimtechnologies/pep-citation-audit

## Why

PEP 12 asks authors to set `Python-Version` to the next *planned* release. When a feature slips,
nothing updates the header automatically. The header feeds peps.python.org and the PEPs API,
which other tools and status clean-ups filter on. A checked list of wrong headers is something
the PEP editors can act on directly. (It turned out there is almost nothing to fix.)

## Run

```
python -m unittest -v
python job.py --out-dir out
```

`job.py` uses only the standard library. It saves the exact snapshot it graded
(`out/snapshot/`, with SHA-256 hashes and the CPython commit in `out/summary.json`), a per-PEP
table (`out/peps.csv`, `out/peps.json`) and the verdicts.

## Method in one paragraph

A PEP is *mentioned* in a What's New page if the page uses `:pep:` with its number or writes
`PEP N`. It is *headlined* if a section title mentions it. For Final Standards Track PEPs with
one 3.x header, the header is compared with the first 3.x release that headlines the PEP (P1a)
and with the first that mentions it at all (P1b). Disagreements are leads, not errors: each is
read by hand before it goes on the fix list. Known limit: a `:ref:` link to another page's PEP
section (as 3.0 does for PEP 3116) is not counted as a mention.
