"""Optimal (OPT / Belady's MIN) page replacement.

Evicts the page whose next use is furthest in the future (or never). It needs
knowledge of the future, so it cannot be implemented in a real OS; it is used
as the theoretical lower bound for the number of page faults.

Efficiency: the "next use" of every position is computed once with a single
backward pass in O(n). Victim selection is then O(frames) per fault, instead of
rescanning the rest of the string (which would be O(n) per fault).
Tie-break: among pages never used again, the earliest loaded is evicted.

Author: Sabina Gasimova
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

from .core import PageReplacementAlgorithm, register

NEVER = math.inf


def next_use_table(references: Sequence[int]) -> List[float]:
    """next_use[i] = index of the next occurrence of references[i] after i (or inf)."""
    table: List[float] = [NEVER] * len(references)
    seen: Dict[int, int] = {}
    for i in range(len(references) - 1, -1, -1):
        table[i] = seen.get(references[i], NEVER)
        seen[references[i]] = i
    return table


@register("optimal")
class Optimal(PageReplacementAlgorithm):
    name = "Optimal (Belady MIN)"
    short_name = "OPT"

    def reset(self, references, frame_count) -> None:
        self.next_use = next_use_table(references)
        self.next_of: Dict[int, float] = {}   # resident page -> next use index
        self.loaded_at: Dict[int, int] = {}

    def on_hit(self, page: int, time: int) -> None:
        self.next_of[page] = self.next_use[time]

    def on_load(self, page: int, time: int, slot: int) -> None:
        self.next_of[page] = self.next_use[time]
        self.loaded_at[page] = time

    def on_evict(self, page: int) -> None:
        self.next_of.pop(page, None)
        self.loaded_at.pop(page, None)

    def choose_victim(self, time: int, slots: List[Optional[int]]) -> int:
        return max(self.next_of, key=lambda p: (self.next_of[p], -self.loaded_at[p]))

    def describe(self, slots) -> str:
        def fmt(v: float) -> str:
            return "∞" if v == NEVER else str(int(v) + 1)  # 1-based step number
        return "sonraki kullanım (adım): " + " ".join(
            f"{p}→{fmt(self.next_of[p])}" for p in slots if p is not None
        )
