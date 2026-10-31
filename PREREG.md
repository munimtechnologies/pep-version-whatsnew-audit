# Pre-registration: do PEP Python-Version headers name the release the feature shipped in?

MV2, Munim, Inc. (mv2@munimtech.com). Filed 2026-10-31, before the data run. Made with AI agents.
Code Apache-2.0; text and results CC BY 4.0.

## Question

PEP 1 says a Standards Track PEP's `Python-Version` header "indicates the version of Python that
the feature will be released with". PEP 12 tells authors to set it to the next *planned* version,
and nothing re-checks it automatically when a feature slips. The checklist for marking a PEP
Final asks a person to confirm "Python-Version is correct" (for example python/peps PR #4943).
CPython's What's New pages (`Doc/whatsnew/X.Y.rst`) are the other record of which release a PEP
shipped in. This study compares the two records for every PEP and lists every disagreement, so
that a maintainer can check and fix each one.

## Prior art (searched 2026-10-31)

- python/peps fixes headers one at a time (issue #2737, missing header on PEP 613; PR #651,
  PEP 539; a 2011 commit adding missing headers to PEPs 342 and 343).
- The status clean-ups (python/peps #2872, #3817, PR #4986; the discuss.python.org threads
  "Multiple released PEPs have status Accepted, not Final" (2022) and "Accepted-but-not-final
  Python 3.12 PEPs?" (2024)) filter on `python_version` and `status`. They do not test whether
  `python_version` is right.
- The PEP linter checks header format, not content.
- Nearest own work: munimtechnologies/pep-lifecycle-census (status timing). It never read What's
  New.
- No systematic cross-check of `Python-Version` against What's New was found.

## Data (fixed before the run)

- `https://peps.python.org/api/peps.json`, fetched once (SHA-256 recorded).
- `Doc/whatsnew/{2.0..2.7,3.0..3.20}.rst` from python/cpython at the `main` commit current at the
  run (SHA recorded; missing files skipped).
- A PEP is *mentioned* in a What's New if the text has `:pep:` with its number (with or without
  link text or an anchor) or `PEP N` / `PEPs N`. It is *headlined* if a section title (an unindented
  line directly above an RST underline) mentions it.
- Version comparisons use the 3.x line only (2.6 and 2.7 back-ported 3.0 and 3.1 features, so
  2.x pages would make 3.x headers look late). The 2.x line is reported separately (descriptive).

## Predictions (bars fixed here, in audit.py)

Sample F: Final, Standards Track PEPs whose header is a single 3.x version.

- **P1a.** Among F PEPs headlined in at least one 3.x What's New, the header equals the first
  3.x release that headlines it in **at least 90%** of cases.
- **P1b (second definition, required because headlined PEPs are the big, well-tracked
  features).** Among F PEPs mentioned anywhere in a 3.x What's New, the header equals the first
  3.x release that mentions it in **at least 90%** of cases.
- **P2.** Among P1b disagreements, **more than half** have a header *earlier* than the first
  mention (the feature slipped and the planned version was never updated).
- **P3.** Among F PEPs whose header release has a What's New page, that page mentions the PEP in
  **at least 80%** of cases.
- **P4.** **At least 3** PEPs are still `Accepted` (not Final), are Standards Track with a single
  3.x header no later than 3.14, and are mentioned in that release's What's New.

## What I knew before the run (how blind each prediction is)

- I have seen the field list of peps.json and about a dozen entries, the 8 PEP section titles of
  What's New in 3.12, and the 2022 and 2024 status threads. I have not counted anything.
- P1a/P1b expectation: about 95% and about 88%. P1b may fail because a page can mention a PEP
  early, before it ships ("will become the default under PEP N"). That would also push P2 the
  other way. P4 is the least blind: the status threads named several such PEPs, but the
  maintainers have cleared many since.

## Grading plan

Every P1a and P1b disagreement, every P3 miss among the 3.10+ headers and every P4 PEP will be
read by hand on peps.python.org and in the What's New text. Each is then labelled: header wrong;
What's New anticipatory or retrospective mention; feature shipped in stages; or parser artefact.
Only "header wrong" cases go on the fix list, and each will be checked against the CPython
changelog or the commit that merged the feature. The verdicts above are computed mechanically and
reported as they come out, including failures.

## Limits

- What's New is itself a record kept by hand. A missing mention can be the What's New's gap, not
  the PEP's.
- PEPs that ship in stages (a `from __future__` import, then a default) have no single right
  version. Their hand-check label says so.
- Text matching can pick up a PEP number in an unrelated sentence. Every listed case is checked
  by hand before it is called an error.
