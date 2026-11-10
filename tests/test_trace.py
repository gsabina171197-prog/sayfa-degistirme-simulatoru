"""Trace reading, instrumented programs and the trace experiment."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import main
from simulator import SimulationError, create
from simulator import trace as tr

ROOT = Path(__file__).resolve().parent.parent


class TraceReadingTests(unittest.TestCase):
    def write(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
        f.write(text)
        f.close()
        self.addCleanup(Path(f.name).unlink)
        return f.name

    def test_lackey_format(self):
        path = self.write("==123== Lackey\nI  00001000,4\n L 00002000,8\n S 00002ff8,8\n M 00003000,4\n")
        t = tr.read_trace(path, 4096)
        self.assertEqual(t.pages(collapse=False), [1, 2, 2, 3])
        self.assertEqual(t.pages(), [1, 2, 3])
        self.assertEqual(tr.read_trace(path, 4096, kinds="LS").pages(), [2])

    def test_plain_format_and_renumbering(self):
        t = tr.read_trace(self.write("0x5000\n20480\n# yorum\n0x1000\n"), 4096)
        self.assertEqual(t.pages(), [5, 1])
        self.assertEqual(t.renumbered(), [0, 1])

    def test_invalid(self):
        with self.assertRaises(SimulationError):
            tr.read_trace(self.write("0x1000\n"), 1000)        # not a power of two
        with self.assertRaises(SimulationError):
            tr.read_trace(self.write("merhaba\n"), 4096)       # nothing readable
        with self.assertRaises(SimulationError):
            tr.read_trace("yok.lackey", 4096)

    def test_sample_trace_file(self):
        t = tr.read_trace(ROOT / "data" / "izler" / "matris_carpim_8.lackey", 256)
        self.assertEqual(len(t.addresses), 8 * 8 * 8 * 2 + 8 * 8)

    def test_write_and_read_back(self):
        t = tr.Trace("x", [0x1000, 0x1008, 0x3000], 4096)
        with tempfile.TemporaryDirectory() as d:
            p = tr.write_lackey(t, Path(d) / "x.lackey", "deneme")
            self.assertEqual(tr.read_trace(p, 4096).addresses, t.addresses)


class InstrumentedProgramTests(unittest.TestCase):
    def test_quicksort_really_sorts(self):
        import random
        rng = random.Random(1)
        log = []
        arr = tr.TracedArray(log, 0x1000, [rng.randrange(100) for _ in range(300)])
        tr.sort_in_place(arr)
        self.assertEqual(arr.data, sorted(arr.data))
        self.assertTrue(all(0x1000 <= a < 0x1000 + 300 * 8 for a in log))
        self.assertEqual(tr.quicksort(200, seed=1), tr.quicksort(200, seed=1))   # reproducible

    def test_row_major_beats_column_major(self):
        rows = tr.program_trace("matris_satir", 512).renumbered()
        cols = tr.program_trace("matris_sutun", 512).renumbered()
        lru = create("lru")
        self.assertEqual(lru.run(rows, 8, record=False).faults, len(set(rows)))   # only cold misses
        self.assertGreater(lru.run(cols, 8, record=False).faults, 10 * len(set(cols)))

    def test_unknown_program(self):
        with self.assertRaises(SimulationError):
            tr.program_trace("bilinmeyen")

    def test_fast_mode_matches_recorded_mode(self):
        refs = tr.program_trace("ikili_arama", 512).renumbered()[:800]
        for key in ("fifo", "lru", "optimal", "clock", "lfu", "aging"):
            a = create(key).run(refs, 6)
            b = create(key).run(refs, 6, record=False)
            self.assertEqual(a.faults, b.faults, key)
            self.assertEqual(a.evictions, b.evictions, key)


class TraceCLITests(unittest.TestCase):
    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = main.main(list(args) + ["--no-color"])
        return code, out.getvalue()

    def test_trace_file_mode(self):
        code, out = self.run_cli("--trace", str(ROOT / "data" / "izler" / "matris_carpim_8.lackey"),
                                 "--page-size", "256", "--frames", "3", "--no-export")
        self.assertEqual(code, 0)
        self.assertIn("uzun", out)            # long input -> summary only
        self.assertIn("Karşılaştırma", out)

    def test_experiment_mode(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = self.run_cli("--experiment", "--range", "1", "4", "--out", d)
            self.assertEqual(code, 0)
            self.assertIn("Özet", out)
            self.assertTrue((Path(d) / "deney_izler.csv").exists())
            self.assertTrue((Path(d) / "deney_quicksort.svg").exists())


if __name__ == "__main__":
    unittest.main()
