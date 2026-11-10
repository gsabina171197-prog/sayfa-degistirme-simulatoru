"""FIFO (First-In, First-Out) page replacement.

The page that has been in memory the longest is evicted, regardless of how
often or how recently it was used. Data structure: collections.deque (O(1)).
FIFO is not a stack algorithm, so it can show Belady's anomaly.

Author: Sabina Gasimova
"""
from __future__ import annotations

from collections import deque
from typing import Deque, List, Optional

from .core import PageReplacementAlgorithm, register


@register("fifo")
class FIFO(PageReplacementAlgorithm):
    name = "First-In First-Out"
    short_name = "FIFO"

    def reset(self, references, frame_count) -> None:
        self.queue: Deque[int] = deque()

    def on_load(self, page: int, time: int, slot: int) -> None:
        self.queue.append(page)

    def choose_victim(self, time: int, slots: List[Optional[int]]) -> int:
        return self.queue.popleft()  # oldest loaded page

    def describe(self, slots) -> str:
        return "kuyruk (eski→yeni): " + " ".join(map(str, self.queue))
