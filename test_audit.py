"""Tests for audit.py; every expected number below is worked out by hand.

MV2, Munim, Inc. Apache-2.0. Made with AI agents.
"""
import unittest

import audit

WN = {
    "2.7": "PEP 100: Backport\n==================\n\nbody\n",
    "3.1": ("What's New In Python 3.1\n************************\n\n"
            "PEP 100: Thing\n==============\n\n"
            "Text mentions PEP 999 and :pep:`the thing <0102>`.\n\n"
            "PEP 106: rejected idea\n----------------------\n\nbody\n"),
    "3.2": ("PEP 101: Late\n-------------\n\n"
            "PEP 105 and PEP 100: Combined\n-----------------------------\n\n"
            "Accepted PEP 104 lands.\n\n"
            "PEP 102: Now\n~~~~~~~~~~~~\n"),
    "index": "PEP 1\n=====\n",
}


def pep(n, status, typ, pv, topic=""):
    return {"number": n, "title": "t%d" % n, "status": status, "type": typ,
            "topic": topic, "python_version": pv}


PEPS = {
    "1": pep(1, "Active", "Process", None),
    "100": pep(100, "Final", "Standards Track", "3.1"),
    "101": pep(101, "Final", "Standards Track", "3.1"),
    "102": pep(102, "Final", "Standards Track", "3.2"),
    "103": pep(103, "Final", "Standards Track", "2.7, 3.1"),
    "104": pep(104, "Accepted", "Standards Track", "3.2"),
    "105": pep(105, "Final", "Standards Track", None),
    "106": pep(106, "Rejected", "Standards Track", "3.1"),
    "107": pep(107, "Final", "Standards Track", "3.2"),
}


class Parsing(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(audit.parse_versions("2.6, 3.0"), [(2, 6), (3, 0)])
        self.assertEqual(audit.parse_versions("3.10"), [(3, 10)])
        self.assertEqual(audit.parse_versions(None), [])
        self.assertEqual(audit.parse_versions("2.x"), [])

    def test_refs(self):
        self.assertEqual(audit.pep_refs(":pep:`695` and :pep:`x <0632#y>`"), {695, 632})
        self.assertEqual(audit.pep_refs("PEPs 484 and PEP 3118-style"), {484, 3118})
        self.assertEqual(audit.pep_refs("Python 3.12 has no peps"), set())

    def test_headings(self):
        self.assertEqual(audit.heading_lines(WN["3.2"]),
                         ["PEP 101: Late", "PEP 105 and PEP 100: Combined", "PEP 102: Now"])
        self.assertEqual(audit.heading_lines("  indented\n----\nx\n= = =\n"), [])

    def test_index(self):
        idx = audit.index_whatsnew(WN)
        self.assertEqual(sorted(idx), [(2, 7), (3, 1), (3, 2)])
        self.assertEqual(idx[(3, 1)]["all"], {100, 999, 102, 106})
        self.assertEqual(idx[(3, 1)]["heads"], {100, 106})
        self.assertEqual(idx[(3, 2)]["heads"], {101, 105, 100, 102})
        self.assertEqual(idx[(3, 2)]["all"], {101, 105, 100, 104, 102})


class Analyze(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = audit.analyze(PEPS, WN)

    def test_counts(self):
        r = self.r
        self.assertEqual(r["n_peps"], 9)
        self.assertEqual(r["whatsnew_versions"], ["2.7", "3.1", "3.2"])
        self.assertEqual(r["n_standards_track"], 8)
        self.assertEqual(r["n_single_3x_header"], 6)  # 100 101 102 104 106 107
        self.assertEqual(r["n_final_single_3x"], 4)   # 100 101 102 107

    def test_p1a(self):
        p = self.r["P1a"]
        self.assertEqual((p["n"], p["match"]), (3, 2))
        self.assertAlmostEqual(p["share"], 2 / 3)
        self.assertEqual(p["verdict"], "FAILED")
        self.assertEqual([m["number"] for m in p["mismatches"]], [101])
        self.assertEqual(p["mismatches"][0]["first_py3_head"], "3.2")

    def test_p1b_p2(self):
        p = self.r["P1b"]
        self.assertEqual((p["n"], p["match"]), (3, 1))
        self.assertEqual([m["number"] for m in p["mismatches"]], [101, 102])
        self.assertEqual(p["verdict"], "FAILED")
        p2 = self.r["P2"]
        self.assertEqual((p2["n"], p2["header_earlier"]), (2, 1))
        self.assertEqual(p2["share"], 0.5)
        self.assertEqual(p2["verdict"], "FAILED")

    def test_p3_p4(self):
        p3 = self.r["P3"]
        self.assertEqual((p3["n"], p3["hit"]), (4, 2))
        self.assertEqual(p3["verdict"], "FAILED")
        self.assertEqual(sorted(m["number"] for m in p3["misses"]), [101, 107])
        p4 = self.r["P4"]
        self.assertEqual(p4["count"], 1)
        self.assertEqual([m["number"] for m in p4["peps"]], [104])
        self.assertEqual(p4["verdict"], "FAILED")

    def test_descriptive(self):
        d = self.r["descriptive"]
        self.assertEqual([m["number"] for m in d["missing_header_headlined"]], [105])
        self.assertEqual([m["number"] for m in d["headlined_inactive"]], [106])
        self.assertEqual(d["multi_version_headers"], 1)
        # 100 (3.1 in heads), 102 (3.2 in heads); 101 headlined only in 3.2
        self.assertAlmostEqual(d["header_headlined_anywhere_share"], 2 / 3)
        self.assertEqual(d["py2_line"], {"n": 0, "match": 0})

    def test_rows_serialise(self):
        row = [x for x in self.r["rows"] if x["number"] == 100][0]
        self.assertEqual(row["heads"], ["2.7", "3.1", "3.2"])
        self.assertEqual(row["first_py3_head"], "3.1")
        self.assertEqual(row["first_py3_mention"], "3.1")

    def test_all_pass(self):
        peps = {"200": pep(200, "Final", "Standards Track", "3.1")}
        r = audit.analyze(peps, {"3.1": "PEP 200: X\n----------\n"})
        for k in ("P1a", "P1b", "P3"):
            self.assertEqual(r[k]["verdict"], "HELD")
        self.assertEqual(r["P2"]["verdict"], "NOT TESTABLE")


if __name__ == "__main__":
    unittest.main()
