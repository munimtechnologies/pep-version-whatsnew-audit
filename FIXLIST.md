# Fix list (confirmed errors only)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name. CC BY 4.0.
Each entry was checked by reading the source text; see GRADING.md for how it was found.

## 1. What's New in Python 3.12 credits the Unstable C API tier to PEP 697 (should be PEP 689)

File: `Doc/whatsnew/3.12.rst` in python/cpython (checked at main commit
`683fca8498053d63a77ff48df9ee47153778a765`, 2026-10-31; also live on
https://docs.python.org/3/whatsnew/3.12.html).

- Release highlights, "C API improvements":
  `* :ref:`PEP 697 <whatsnew312-pep697>`, unstable C API tier`
- C API Changes, New Features:
  `.. _whatsnew312-pep697:` then `* :pep:`697`: Introduce the :ref:`Unstable C API tier <unstable-c-api>`, ...`

Evidence:
- PEP 689 is titled "Unstable C API tier" (Final, Python-Version 3.12):
  https://peps.python.org/pep-0689/
- PEP 697 is "Limited C API for Extending Opaque Types". The same What's New file describes that
  feature correctly a few lines later (`* :pep:`697`: Add an API for extending types whose instance
  memory layout is opaque`).
- The tracking issue is python/cpython#91744, "PEP 689 -- Add an unstable C-API tier".

Suggested fix: change `697` to `689` in the two lines above (and rename the label to
`whatsnew312-pep689` in both places, or leave the label as is).

Status: not yet reported upstream as of 2026-10-31 (searched python/cpython issues and PRs for
"PEP 689" whatsnew, "PEP 697" unstable, and "unstable C API tier" whatsnew).

## Candidates (not errors; listed for completeness)

- PEP 453 has no `Python-Version` header; its text and the 3.4 What's New point to 3.4.
- PEP 3156's header says 3.3 while asyncio entered the stdlib in 3.4; the PEP itself targets 3.3 via
  PyPI, so this is a judgement call, not an error.
- PEP 739 is still Accepted after shipping in 3.14; python/peps PR #4629 already proposes Final.
