"""Comparisons and analyses built on top of the common interface.

* frame-range analysis: faults of every algorithm for k = lo..hi frames
* automatic Belady anomaly detection (faults increase when frames increase)
* Optimal lower-bound check
* performance analysis on different workload types

Author: Sabina Gasimova
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from .core import SimulationError, available_algorithms, create
from .input_io import WORKLOADS, generate


@dataclass(frozen=True)
class Anomaly:
    algorithm: str
    frames_before: int
    frames_after: int
    faults_before: int
    faults_after: int


def frame_range(references: Sequence[int], lo: int, hi: int,
                keys: Optional[Sequence[str]] = None) -> Dict[str, List[int]]:
    """{algorithm short name: [faults for lo, lo+1, ..., hi]}"""
    if lo < 1 or hi < lo:
        raise SimulationError("Çerçeve aralığı geçersiz: 1 ≤ başlangıç ≤ bitiş olmalıdır.")
    keys = list(keys) if keys else available_algorithms()
    table: Dict[str, List[int]] = {}
    for key in keys:
        algo = create(key)
        table[algo.short_name] = [algo.run(references, k).faults for k in range(lo, hi + 1)]
    return table


def detect_belady(table: Dict[str, List[int]], lo: int) -> List[Anomaly]:
    found: List[Anomaly] = []
    for name, faults in table.items():
        for i in range(1, len(faults)):
            if faults[i] > faults[i - 1]:
                found.append(Anomaly(name, lo + i - 1, lo + i, faults[i - 1], faults[i]))
    return found


def optimal_is_lower_bound(table: Dict[str, List[int]]) -> bool:
    opt = table.get("OPT")
    if opt is None:
        return True
    return all(all(o <= x for o, x in zip(opt, faults)) for faults in table.values())


@dataclass
class WorkloadReport:
    workload: str
    references: List[int]
    lo: int
    hi: int
    table: Dict[str, List[int]]

    def average_fault_ratio(self) -> Dict[str, float]:
        n = len(self.references)
        return {a: sum(f) / (len(f) * n) for a, f in self.table.items()}

    def gap_to_optimal(self) -> Dict[str, float]:
        """Average extra faults relative to OPT, in percent."""
        opt = self.table["OPT"]
        out = {}
        for a, faults in self.table.items():
            ratios = [(x - o) / o for x, o in zip(faults, opt) if o]
            out[a] = 100 * sum(ratios) / len(ratios) if ratios else 0.0
        return out


def workload_analysis(length: int, pages: int, lo: int, hi: int, seed: int,
                      kinds: Sequence[str] = WORKLOADS,
                      keys: Optional[Sequence[str]] = None) -> List[WorkloadReport]:
    reports = []
    for i, kind in enumerate(kinds):
        refs = generate(kind, length, pages, seed + i)
        reports.append(WorkloadReport(kind, refs, lo, hi, frame_range(refs, lo, hi, keys)))
    return reports
