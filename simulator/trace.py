"""Memory-access traces: from byte addresses to page reference strings.

1. Reading trace files
   * Valgrind Lackey format (`valgrind --tool=lackey --trace-mem=yes prog`):
         I  0400d7d4,8      instruction fetch
          L 04222cac,8      load
          S 04222cb0,4      store
          M 0421c7f0,4      modify (load + store)
   * Plain format: one address per line, hexadecimal (0x...) or decimal.
   The page number is address // page_size. Consecutive references to the same
   page can optionally be collapsed. This preserves many policies' page-fault
   counts but can change frequency/aging-dependent behavior (LFU, Aging).
   Use --no-collapse when studying those details.

2. Instrumented example programs
   Small, real algorithms (matrix traversal, matrix multiply, quicksort, binary
   search) run on arrays that record the virtual address of every element they
   touch. This produces genuine access patterns with known locality, without
   needing an external tracer.

Author: Sabina Gasimova
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from .core import SimulationError

_LACKEY = re.compile(r"^\s*([ILSM])\s+([0-9a-fA-F]+),(\d+)")
_PLAIN = re.compile(r"^\s*(0[xX][0-9a-fA-F]+|\d+)\s*$")


@dataclass
class Trace:
    name: str
    addresses: List[int]
    page_size: int

    def pages(self, collapse: bool = True) -> List[int]:
        out: List[int] = []
        for a in self.addresses:
            p = a // self.page_size
            if not (collapse and out and out[-1] == p):
                out.append(p)
        return out

    def renumbered(self, collapse: bool = True) -> List[int]:
        """Pages renamed 0,1,2... in order of first use (easier to read)."""
        ids: Dict[int, int] = {}
        return [ids.setdefault(p, len(ids)) for p in self.pages(collapse)]


def read_trace(path: str, page_size: int = 4096, kinds: str = "ILSM") -> Trace:
    if page_size < 1 or page_size & (page_size - 1):
        raise SimulationError("Sayfa boyutu 2'nin kuvveti olmalıdır (ör. 4096).")
    p = Path(path)
    if not p.is_file():
        raise SimulationError(f"İz dosyası bulunamadı: {path}")
    addrs: List[int] = []
    with p.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip() or line.startswith(("==", "#")):
                continue
            m = _LACKEY.match(line)
            if m:
                if m.group(1) in kinds:
                    addrs.append(int(m.group(2), 16))
                continue
            m = _PLAIN.match(line)
            if m:
                addrs.append(int(m.group(1), 0))
    if not addrs:
        raise SimulationError(f"{p.name}: okunabilir adres bulunamadı.")
    return Trace(p.stem, addrs, page_size)


def write_lackey(trace: Trace, path: str, comment: str = "") -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        if comment:
            f.write(f"# {comment}\n")
        for a in trace.addresses:
            f.write(f" L {a:08x},8\n")
    return p


# ---- instrumented programs ---------------------------------------------------
class TracedArray:
    """A list whose element accesses are logged as virtual addresses."""

    def __init__(self, log: List[int], base: int, data: Iterable, elem_size: int = 8):
        self.log, self.base, self.size = log, base, elem_size
        self.data = list(data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, i: int):
        self.log.append(self.base + i * self.size)
        return self.data[i]

    def __setitem__(self, i: int, v) -> None:
        self.log.append(self.base + i * self.size)
        self.data[i] = v


BASE_A, BASE_B, BASE_C = 0x10000000, 0x20000000, 0x30000000


def matrix_rows(n: int = 48) -> List[int]:
    """Sum of an n×n matrix, row by row (row-major storage: sequential)."""
    log: List[int] = []
    m = TracedArray(log, BASE_A, range(n * n))
    total = 0
    for i in range(n):
        for j in range(n):
            total += m[i * n + j]
    return log


def matrix_columns(n: int = 48) -> List[int]:
    """Same sum, column by column: every access jumps n elements ahead."""
    log: List[int] = []
    m = TracedArray(log, BASE_A, range(n * n))
    total = 0
    for j in range(n):
        for i in range(n):
            total += m[i * n + j]
    return log


def matrix_multiply(n: int = 20) -> List[int]:
    """C = A × B with the naive i-j-k loop (B is walked column-wise)."""
    log: List[int] = []
    a = TracedArray(log, BASE_A, range(n * n))
    b = TracedArray(log, BASE_B, range(n * n))
    c = TracedArray(log, BASE_C, [0] * (n * n))
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s += a[i * n + k] * b[k * n + j]
            c[i * n + j] = s
    return log


def sort_in_place(arr) -> None:
    """Iterative quicksort with Lomuto partition (works on any indexable)."""

    def part(lo: int, hi: int) -> int:
        pivot = arr[hi]
        i = lo
        for j in range(lo, hi):
            if arr[j] < pivot:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        return i

    stack = [(0, len(arr) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo < hi:
            p = part(lo, hi)
            stack.append((lo, p - 1))
            stack.append((p + 1, hi))


def quicksort(n: int = 3000, seed: int = 361) -> List[int]:
    """Quicksort on n random integers; returns the address trace."""
    log: List[int] = []
    rng = random.Random(seed)
    sort_in_place(TracedArray(log, BASE_A, (rng.randrange(10 ** 6) for _ in range(n))))
    return log


def binary_search(n: int = 20000, queries: int = 400, seed: int = 361) -> List[int]:
    """Repeated binary searches in a sorted array: a few hot pages (the
    first probes) and many cold ones."""
    log: List[int] = []
    rng = random.Random(seed)
    arr = TracedArray(log, BASE_A, range(0, 2 * n, 2))
    for _ in range(queries):
        x = rng.randrange(2 * n)
        lo, hi = 0, n - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            v = arr[mid]
            if v == x:
                break
            if v < x:
                lo = mid + 1
            else:
                hi = mid - 1
    return log


PROGRAMS: Dict[str, Tuple[str, Callable[[], List[int]]]] = {
    "matris_satir": ("Matris toplamı, satır satır", matrix_rows),
    "matris_sutun": ("Matris toplamı, sütun sütun", matrix_columns),
    "matris_carpim": ("Matris çarpımı (i-j-k)", matrix_multiply),
    "quicksort": ("Quicksort", quicksort),
    "ikili_arama": ("Tekrarlı ikili arama", binary_search),
}


def program_trace(key: str, page_size: int = 512) -> Trace:
    if key not in PROGRAMS:
        raise SimulationError(f"Bilinmeyen program: {key}. Seçenekler: {', '.join(PROGRAMS)}")
    return Trace(key, PROGRAMS[key][1](), page_size)
