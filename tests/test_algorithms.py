"""Algorithm correctness tests.

Expected values for the group scenario are worked out step by step in
docs/adim_adim_cozum.md. Random scenarios are cross-checked against small,
independent "naive" implementations written differently from the real ones.
"""
import random
import unittest

from simulator import SimulationError, create, run_all
from simulator.optimal import NEVER, next_use_table

GROUP = [3, 5, 3, 0, 5, 6, 5, 1, 5, 1, 3, 1, 4, 2, 1, 0, 5, 2, 0, 5]
TEXTBOOK = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]


# ---- independent naive reference implementations ---------------------------
def naive_fifo(refs, k):
    mem, faults = [], 0
    for p in refs:
        if p not in mem:
            faults += 1
            if len(mem) == k:
                mem.pop(0)
            mem.append(p)
    return faults


def naive_lru(refs, k):
    mem, last, faults = set(), {}, 0
    for t, p in enumerate(refs):
        if p not in mem:
            faults += 1
            if len(mem) == k:
                mem.remove(min(mem, key=lambda q: last[q]))
            mem.add(p)
        last[p] = t
    return faults


def naive_opt(refs, k):
    mem, faults = [], 0
    for t, p in enumerate(refs):
        if p in mem:
            continue
        faults += 1
        if len(mem) == k:
            future = refs[t + 1:]
            mem.remove(max(mem, key=lambda q: future.index(q) if q in future else 10 ** 9))
        mem.append(p)
    return faults


def faults(key, refs, k):
    return create(key).run(refs, k).faults


class GroupScenarioTests(unittest.TestCase):
    """Our own scenario: 20 references, 3 frames."""

    def test_fifo(self):
        self.assertEqual(faults("fifo", GROUP, 3), 13)

    def test_lru(self):
        self.assertEqual(faults("lru", GROUP, 3), 11)

    def test_optimal(self):
        self.assertEqual(faults("optimal", GROUP, 3), 8)

    def test_clock(self):
        self.assertEqual(faults("clock", GROUP, 3), 12)

    def test_lfu(self):
        self.assertEqual(faults("lfu", GROUP, 3), 10)

    def test_aging(self):
        self.assertEqual(faults("aging", GROUP, 3), 12)

    def test_fifo_eviction_sequence(self):
        evicted = [s.evicted for s in create("fifo").run(GROUP, 3).steps if s.evicted is not None]
        self.assertEqual(evicted, [3, 5, 0, 6, 1, 5, 3, 4, 2, 1])

    def test_optimal_evicts_furthest_next_use(self):
        steps = create("optimal").run(GROUP, 3).steps
        self.assertEqual(steps[5].evicted, 0)   # step 6: 0 next used at step 16
        self.assertEqual(steps[12].evicted, 3)  # step 13: 3 never used again

    def test_lru_evicts_least_recent(self):
        steps = create("lru").run(GROUP, 3).steps
        self.assertEqual(steps[5].evicted, 3)   # step 6: 3 last used at step 3


class TextbookTests(unittest.TestCase):
    """Silberschatz, Operating System Concepts — published results."""

    def test_textbook_values(self):
        got = {r.short_name: r.faults for r in run_all(TEXTBOOK, 3, ["fifo", "lru", "optimal"])}
        self.assertEqual(got, {"FIFO": 15, "LRU": 12, "OPT": 9})


class ClockTests(unittest.TestCase):
    def test_second_chance_saves_referenced_page(self):
        # 1 2 3 fill; 1 is hit; then 4: hand clears 1,2,3 bits and evicts 1 (FIFO
        # degenerate case); afterwards 2 has bit 0 -> next fault evicts 2.
        r = create("clock").run([1, 2, 3, 1, 4, 5], 3)
        self.assertEqual([s.evicted for s in r.steps[4:]], [1, 2])

    def test_clock_with_hits_differs_from_fifo(self):
        refs = [1, 2, 3, 2, 4, 2, 5, 2, 1]
        self.assertLess(faults("clock", refs, 3), faults("fifo", refs, 3))


class AgingTests(unittest.TestCase):
    def test_counter_shift_on_tick(self):
        from simulator.aging import Aging
        algo = Aging(bits=8, period=1)
        r = algo.run([1, 2, 1], 2)
        # after 3 ticks: 1 referenced at t0 and t2 -> 10100000, 2 at t1 -> 01000000
        self.assertIn("1:0|10100000", r.steps[-1].note)
        self.assertIn("2:0|01000000", r.steps[-1].note)

    def test_evicts_oldest_history(self):
        r = create("aging").run([1, 2, 1, 1, 3], 2)
        self.assertEqual(r.steps[-1].evicted, 2)

    def test_long_history_aging_equals_lru(self):
        from simulator.aging import Aging
        rng = random.Random(5)
        for _ in range(100):
            refs = [rng.randrange(6) for _ in range(rng.randint(1, 30))]
            k = rng.randint(1, 5)
            self.assertEqual(Aging(bits=64, period=1).run(refs, k).faults, naive_lru(refs, k), (refs, k))

    def test_invalid_parameters(self):
        from simulator.aging import Aging
        with self.assertRaises(ValueError):
            Aging(bits=0)


class LFUTests(unittest.TestCase):
    def test_tie_broken_by_load_order(self):
        r = create("lfu").run([1, 2, 3, 4], 3)
        self.assertEqual(r.steps[3].evicted, 1)

    def test_frequent_page_survives(self):
        r = create("lfu").run([1, 1, 1, 2, 3, 4, 5], 3)
        self.assertIn(1, r.steps[-1].frames)


class EdgeCaseTests(unittest.TestCase):
    ALGOS = ["fifo", "lru", "optimal", "clock", "lfu", "aging"]

    def test_single_frame_faults_on_every_change(self):
        refs = [1, 1, 2, 2, 1, 3, 3, 3, 1]
        for key in self.ALGOS:
            self.assertEqual(faults(key, refs, 1), 5, key)

    def test_enough_frames_only_compulsory_faults(self):
        for key in self.ALGOS:
            self.assertEqual(faults(key, GROUP, len(set(GROUP))), len(set(GROUP)), key)
            self.assertEqual(faults(key, GROUP, 50), len(set(GROUP)), key)

    def test_single_reference(self):
        for key in self.ALGOS:
            r = create(key).run([42], 3)
            self.assertEqual((r.total, r.faults, r.hits), (1, 1, 0))

    def test_all_same_page(self):
        for key in self.ALGOS:
            self.assertEqual(faults(key, [7] * 10, 2), 1)

    def test_hits_plus_faults_equals_total(self):
        for r in run_all(GROUP, 3):
            self.assertEqual(r.hits + r.faults, r.total)
            self.assertAlmostEqual(r.hit_ratio + r.fault_ratio, 1.0)

    def test_frames_never_exceed_capacity_and_no_duplicates(self):
        for r in run_all(GROUP, 3):
            for s in r.steps:
                resident = [p for p in s.frames if p is not None]
                self.assertEqual(len(resident), len(set(resident)))
                self.assertIn(s.page, s.frames)

    def test_invalid_inputs(self):
        for key in self.ALGOS:
            algo = create(key)
            with self.assertRaises(SimulationError):
                algo.run([], 3)
            with self.assertRaises(SimulationError):
                algo.run([1, 2], 0)
            with self.assertRaises(SimulationError):
                algo.run([1, -2], 3)
            with self.assertRaises(SimulationError):
                algo.run([1, 2], 2.5)

    def test_unknown_algorithm(self):
        with self.assertRaises(SimulationError):
            create("mru")


class RandomCrossCheckTests(unittest.TestCase):
    """200 reproducible random scenarios."""

    def scenarios(self, n=200):
        rng = random.Random(361)
        for _ in range(n):
            pages = rng.randint(2, 10)
            refs = [rng.randrange(pages) for _ in range(rng.randint(1, 40))]
            yield refs, rng.randint(1, 6)

    def test_against_naive_implementations(self):
        for refs, k in self.scenarios():
            self.assertEqual(faults("fifo", refs, k), naive_fifo(refs, k))
            self.assertEqual(faults("lru", refs, k), naive_lru(refs, k))
            self.assertEqual(faults("optimal", refs, k), naive_opt(refs, k))

    def test_optimal_is_lower_bound(self):
        for refs, k in self.scenarios():
            opt = faults("optimal", refs, k)
            for key in ("fifo", "lru", "clock", "lfu", "aging"):
                self.assertLessEqual(opt, faults(key, refs, k), (key, refs, k))

    def test_stack_algorithms_never_show_belady(self):
        for refs, _ in self.scenarios(100):
            for key in ("lru", "optimal"):
                series = [faults(key, refs, k) for k in range(1, 8)]
                self.assertEqual(series, sorted(series, reverse=True), (key, refs))


class NextUseTableTests(unittest.TestCase):
    def test_single_backward_pass(self):
        self.assertEqual(next_use_table([1, 2, 1, 3, 2]), [2, 4, NEVER, NEVER, NEVER])

    def test_matches_brute_force(self):
        rng = random.Random(7)
        refs = [rng.randrange(5) for _ in range(60)]
        brute = [next((j for j in range(i + 1, len(refs)) if refs[j] == refs[i]), NEVER)
                 for i in range(len(refs))]
        self.assertEqual(next_use_table(refs), brute)


if __name__ == "__main__":
    unittest.main()
