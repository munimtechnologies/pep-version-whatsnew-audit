# pep-version-whatsnew-audit

Does each Python PEP's `Python-Version` header name the release its feature actually shipped in?
This audit checks every PEP in https://peps.python.org/api/peps.json against CPython's own
"What's New in Python X.Y" pages and lists each disagreement for a person to check.

By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Code Apache-2.0; text and results
CC BY 4.0.

## Status

- 2026-10-31: pre-registered (PREREG.md) before any data was downloaded. Five predictions, bars
  fixed in `audit.py`. Results and a hand-checked fix list will be added here once the data run
  finishes, including any predictions that fail.

## Why

PEP 12 asks authors to set `Python-Version` to the next *planned* release. When a feature slips,
nothing updates the header automatically. The header feeds peps.python.org and the PEPs API,
which other tools and status clean-ups filter on. A checked list of wrong headers is something
the PEP editors can act on directly.

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
read by hand before it goes on the fix list.
