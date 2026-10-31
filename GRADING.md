# Grading of run 1 (pep-version-audit-v1)

MV2, Munim, Inc. (mv2@munimtech.com). Graded 2026-10-31. Made with AI agents working in MV2's name.
Text CC BY 4.0.

Data: peps.json (747 PEPs, SHA-256 `bb8fea4b...1ecd`) and CPython `Doc/whatsnew/` at commit
`683fca8498053d63a77ff48df9ee47153778a765`, fetched 2026-10-31 18:59 UTC. The full numbers are in
`results/run1-summary.json`, with one row per PEP in `results/peps.csv`.

## Mechanical verdicts (computed by `audit.py`, bars fixed in PREREG.md)

| Prediction | Bar | Result | Verdict |
|---|---|---|---|
| P1a header = first 3.x release that headlines the PEP | >= 90% | 100 of 102 (98.0%) | HELD |
| P1b header = first 3.x release that mentions the PEP | >= 90% | 182 of 186 (97.8%) | HELD |
| P2 more than half of P1b disagreements have the header earlier | > 50% | 2 of 4 (50%) | FAILED |
| P3 the header release's What's New mentions the PEP | >= 80% | 184 of 201 (91.5%) | HELD |
| P4 at least 3 shipped PEPs (header <= 3.14) still Accepted | >= 3 | 1 | FAILED |

## Hand labels (every case the plan said would be read)

Each case was read in the What's New text in the snapshot and on peps.python.org.

### P1a disagreements (2): neither is a header error

- **PEP 594** (header 3.11, first headlined 3.13). The work was staged: modules were deprecated in 3.11
  (the 3.11 page mentions it but has no PEP 594 section title) and removed in 3.13. *Shipped in
  stages.*
- **PEP 3118** (header 3.0, first headlined 3.3). The new buffer API shipped in 3.0 (and 2.6). In
  3.3 the memoryview rewrite got its own section. *Shipped in stages.*

### P1b disagreements (4): no confirmed header error, one debatable

- **PEP 624** (header 3.11, first mention 3.10). The 3.10 page lists it under "Important
  deprecations, removals or restrictions" before the removal; the 3.11 page records the removal.
  *Mentioned before it shipped.* The header is right.
- **PEP 706** (header 3.12, first mention 3.8). The tarfile extraction filter was backported as a
  security feature, and the 3.8 to 3.11 pages record those backports. *Backport.* The header is right.
- **PEP 3116** (header 3.0, first mention 3.1). The 3.0 page does cite it, but through
  `:ref:`pep-3116`` (a link to the 2.6 section), which the audit's pattern does not count.
  *Parser artefact.* The header is right.
- **PEP 3156** (header 3.3, asyncio first in the 3.4 stdlib). The PEP says the work starts at
  Python 3.3, which was served from PyPI ("tulip"); the module entered the standard library in 3.4.
  *Debatable.* Not put on the fix list.

So after reading, **0 of 186** checked headers are confirmed wrong (1 debatable). Corrected for the
parser artefact, P1b agreement is 183 of 186 (98.4%).

### Why P2 failed

Too few disagreements were left to test whether slipped features keep their planned version. None
of the four is a slipped feature: one comes from an early mention, one from a backport, one from a
parser artefact, and one is debatable. The prediction assumed that slips leave stale headers. The
data shows the opposite: headers of Final PEPs were corrected by the time they were marked Final.
That fits the Final checklist step that asks a person to confirm "Python-Version is correct".

### P3 misses with header 3.10 or later (3)

- **PEP 687** (3.12, "Isolating modules in the standard library"). This is an umbrella PEP whose
  work ran over several releases. The 3.12 page does not name it. *What's New gap, not an error.*
- **PEP 689** (3.12, "Unstable C API tier"). **The 3.12 What's New credits this feature to the wrong
  PEP.** It says "PEP 697, unstable C API tier" in the release highlights and
  ":pep:`697`: Introduce the Unstable C API tier" under C API changes. PEP 697 is "Limited C API for
  Extending Opaque Types", a different 3.12 feature that is correctly described a few lines later
  under the same number. The tracking issue (python/cpython#91744, "PEP 689 -- Add an
  unstable C-API tier") gives PEP 689. This is
  **a confirmed What's New error** (see FIXLIST.md).
- **PEP 721** (3.12, "Using tarfile.data_filter for source distribution extraction"). This is a
  packaging PEP for tools, and its CPython part is PEP 706's filter. *Out of scope, no error.*

The 14 earlier misses are mostly Python 3000 PEPs (3106, 3112, 3119, 3127, 3129, 3137, 3141) whose
3.0 page describes the change without citing the PEP number, plus PEPs 383, 415 and 417 (features
described without the number) and packaging PEPs 425 and 561. These were not hand-graded (the
plan covers 3.10+ only) and are not claimed as errors.

### P4 (1 PEP): already being handled

**PEP 739** (`build-details.json`, header 3.14) is still Accepted, though 3.14 ships the file.
python/peps PR #4629 "PEP 739: Mark as Final" has been open since 2025-10-04. Nothing to add. P4
failed because the 2022-2025 status clean-ups worked.

### Missing header (descriptive)

**PEP 453** (ensurepip) is Final with no `Python-Version` header, though its text says the code
changes were accepted for 3.4, and the 3.4 page has a PEP 453 section. It is a candidate to add
`Python-Version: 3.4` (low priority; not filed).

## Exploratory follow-up (not pre-registered; labelled as such)

After P3 surfaced the PEP 689/697 mix-up, every PEP citation in a 3.x What's New section title or
summary/feature bullet (`PEP N: ...`, `* :pep:`N`: ...`, `* :ref:`PEP N <...>`, ...`) was read by
hand against the PEP titles in the snapshot: about 230 lines across 3.0 to 3.15. **No other wrong
number was found.** A mechanical version of this check over the whole `Doc/` tree is pre-registered
separately in munimtechnologies/pep-citation-audit.

## Bottom line

PEP `Python-Version` headers are a well-kept record: no confirmed error among 186 Final PEPs that
What's New mentions. The one concrete error this audit found is on the other side, in What's New
3.12, which credits the Unstable C API tier to PEP 697 instead of PEP 689.
