"""LFU (Least Frequently Used) page replacement.

Evicts the resident page with the smallest access count. Ties are broken by
FIFO order (the page loaded earliest leaves first), which keeps the result
deterministic. The counter is reset when a page leaves memory.

Author: Sabina Gasimova
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .core import PageReplacementAlgorithm, register


@register("lfu")
class LFU(PageReplacementAlgorithm):
    name = "Least Frequently Used"
    short_name = "LFU"

    def reset(self, references, frame_count) -> None:
        self.count: Dict[int, int] = {}
        self.loaded_at: Dict[int, int] = {}

    def on_hit(self, page: int, time: int) -> None:
        self.count[page] += 1

    def on_load(self, page: int, time: int, slot: int) -> None:
        self.count[page] = 1
        self.loaded_at[page] = time

    def on_evict(self, page: int) -> None:
        self.count.pop(page, None)
        self.loaded_at.pop(page, None)

    def choose_victim(self, time: int, slots: List[Optional[int]]) -> int:
        return min(self.count, key=lambda p: (self.count[p], self.loaded_at[p]))

    def describe(self, slots) -> str:
        return "sayaç: " + " ".join(f"{p}×{self.count[p]}" for p in slots if p is not None)
