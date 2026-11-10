"""LRU (Least Recently Used) page replacement.

Evicts the page whose last use is furthest in the past. Data structure:
collections.OrderedDict kept in recency order; a hit moves the page to the
end (most recent) and the victim is always the first key - all O(1).
LRU is a stack algorithm, so it never shows Belady's anomaly.

Author: Sabina Gasimova
"""
from __future__ import annotations

from collections import OrderedDict
from typing import List, Optional

from .core import PageReplacementAlgorithm, register


@register("lru")
class LRU(PageReplacementAlgorithm):
    name = "Least Recently Used"
    short_name = "LRU"

    def reset(self, references, frame_count) -> None:
        self.recency: "OrderedDict[int, int]" = OrderedDict()  # page -> last use time

    def on_hit(self, page: int, time: int) -> None:
        self.recency[page] = time
        self.recency.move_to_end(page)

    def on_load(self, page: int, time: int, slot: int) -> None:
        self.recency[page] = time

    def on_evict(self, page: int) -> None:
        self.recency.pop(page, None)

    def choose_victim(self, time: int, slots: List[Optional[int]]) -> int:
        return next(iter(self.recency))  # least recently used

    def describe(self, slots) -> str:
        return "eski→yeni kullanım: " + " ".join(map(str, self.recency))
