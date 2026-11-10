"""Input handling, analysis, export and CLI integration tests."""
import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

import main
from simulator import SimulationError, run_all
from simulator.analysis import (detect_belady, frame_range, optimal_is_lower_bound,
                                workload_analysis)
from simulator.export import (svg_line_chart, write_range_csv, write_steps_csv,
                              write_summary_csv)
from simulator.input_io import WORKLOADS, generate, parse_references, read_reference_file

ROOT = Path(__file__).resolve().parent.parent
BELADY = [5, 2, 3, 4, 5, 2, 1, 5, 2, 3, 2, 4, 1]


class InputTests(unittest.TestCase):
    def test_parse_separators_and_comments(self):
        self.assertEqual(parse_references("1, 2;3\n# yorum\n4 5 # son\n"), [1, 2, 3, 4, 5])

    def test_parse_rejects_bad_values(self):
        for bad in ("", "# sadece yorum", "1 2 x", "1 -3", "1.5 2"):
            with self.assertRaises(SimulationError, msg=bad):
                parse_references(bad)

    def test_read_sample_files(self):
        self.assertEqual(len(read_reference_file(ROOT / "data" / "ornek.txt")), 20)
        self.assertEqual(read_reference_file(ROOT / "data" / "belady.txt"), BELADY)

    def test_missing_and_invalid_file(self):
        with self.assertRaises(SimulationError):
            read_reference_file("yok/boyle_bir_dosya.txt")
        with self.assertRaises(SimulationError):
            read_reference_file(ROOT / "data" / "hatali_ornek.txt")

    def test_generators_are_reproducible(self):
        for kind in WORKLOADS:
            a, b = generate(kind, 50, 8, 99), generate(kind, 50, 8, 99)
            self.assertEqual(a, b)
            self.assertEqual(len(a), 50)
            self.assertTrue(all(0 <= p < 8 for p in a))
        self.assertNotEqual(generate("uniform", 50, 8, 1), generate("uniform", 50, 8, 2))

    def test_generator_validation(self):
        with self.assertRaises(SimulationError):
            generate("uniform", 0, 5)
        with self.assertRaises(SimulationError):
            generate("bilinmeyen", 10, 5)


class AnalysisTests(unittest.TestCase):
    def test_belady_detected_for_fifo_only(self):
        table = frame_range(BELADY, 1, 6, ["fifo", "lru", "optimal"])
        self.assertEqual(table["FIFO"][2:4], [9, 10])
        found = detect_belady(table, 1)
        self.assertEqual([(a.algorithm, a.frames_before, a.frames_after) for a in found],
                         [("FIFO", 3, 4)])

    def test_optimal_lower_bound_check(self):
        self.assertTrue(optimal_is_lower_bound(frame_range(BELADY, 1, 6)))
        self.assertFalse(optimal_is_lower_bound({"OPT": [5], "FIFO": [4]}))

    def test_invalid_range(self):
        with self.assertRaises(SimulationError):
            frame_range(BELADY, 0, 3)
        with self.assertRaises(SimulationError):
            frame_range(BELADY, 4, 2)

    def test_workload_analysis_shape(self):
        reports = workload_analysis(60, 6, 2, 5, seed=1)
        self.assertEqual([r.workload for r in reports], list(WORKLOADS))
        for rep in reports:
            self.assertEqual(len(rep.table["OPT"]), 4)
            self.assertTrue(all(v >= 0 for v in rep.gap_to_optimal().values()))

    def test_loop_workload_lru_worst_case(self):
        # Cyclic scan larger than memory: LRU/FIFO fault on every reference.
        refs = generate("loop", 40, 5)
        self.assertEqual(frame_range(refs, 4, 4, ["lru"])["LRU"], [40])


class ExportTests(unittest.TestCase):
    def test_csv_and_svg_files(self):
        results = run_all([3, 5, 3, 0, 5, 6], 3)
        table = frame_range(BELADY, 1, 6)
        with tempfile.TemporaryDirectory() as d:
            steps = write_steps_csv(results, d)
            summary = write_summary_csv(results, d)
            rng = write_range_csv(table, 1, d)
            with steps.open(encoding="utf-8-sig") as f:
                rows = list(csv.reader(f, delimiter=";"))
            self.assertEqual(len(rows), 1 + 6 * len(results))
            with summary.open(encoding="utf-8-sig") as f:
                self.assertEqual(len(list(csv.DictReader(f, delimiter=";"))), len(results))
            self.assertIn("cerceve;FIFO", rng.read_text(encoding="utf-8-sig"))
        svg = svg_line_chart(table, 1, "Test", anomalies=detect_belady(table, 1))
        self.assertTrue(svg.startswith("<svg") and svg.endswith("</svg>"))
        self.assertIn("Belady", svg)


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main.main(list(args) + ["--no-color"])
        return code, out.getvalue(), err.getvalue()

    def test_full_run_writes_all_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            code, out, _ = self.run_cli("--file", str(ROOT / "data" / "ornek.txt"),
                                        "--frames", "3", "--out", d)
            self.assertEqual(code, 0)
            self.assertIn("Karşılaştırma", out)
            for name in ("adimlar.csv", "ozet.csv", "sonuclar.json", "calisma_logu.txt", "rapor.html"):
                self.assertTrue((Path(d) / name).exists(), name)
            data = json.loads((Path(d) / "sonuclar.json").read_text(encoding="utf-8"))
            faults = {a["algoritma"]: a["sayfa_hatasi"] for a in data["algoritmalar"]}
            self.assertEqual(faults, {"FIFO": 13, "LRU": 11, "OPT": 8, "CLOCK": 12, "LFU": 10, "AGING": 12})

    def test_html_report_is_self_contained(self):
        with tempfile.TemporaryDirectory() as d:
            self.run_cli("--file", str(ROOT / "data" / "belady.txt"), "--frames", "3", "--out", d)
            html = (Path(d) / "rapor.html").read_text(encoding="utf-8")
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn("Belady anomalisi", html)          # detected in the 1..5 frame range
        self.assertNotIn("http://", html.replace('xmlns="http://www.w3.org/2000/svg"', ""))
        self.assertNotIn("https://", html)               # works offline

    def test_menu_definitions_are_valid(self):
        for _, argv in main.MENU:
            args = main.build_parser().parse_args(argv)
            self.assertTrue(args.file or args.workloads or args.experiment or args.trace)

    def test_range_mode_reports_belady(self):
        with tempfile.TemporaryDirectory() as d:
            code, out, _ = self.run_cli("--file", str(ROOT / "data" / "belady.txt"),
                                        "--range", "1", "6", "--out", d)
            self.assertEqual(code, 0)
            self.assertIn("Belady anomalisi tespit edildi", out)
            self.assertTrue((Path(d) / "grafik_cerceve_hata.svg").exists())

    def test_errors_return_code_2(self):
        code, _, err = self.run_cli("--refs", "1 2 x", "--frames", "3", "--no-export")
        self.assertEqual(code, 2)
        self.assertIn("tam sayı değil", err)
        code, _, err = self.run_cli("--refs", "1 2 3", "--frames", "0", "--no-export")
        self.assertEqual(code, 2)
        code, _, _ = self.run_cli("--refs", "1 2 3", "--no-export")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
