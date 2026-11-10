"""Second Chance (Clock) page replacement.

An approximation of LRU used by real kernels. Frames form a circular list with
a "hand". Each resident page has a reference bit, set to 1 on every access.
On a fault the hand moves forward: a page with bit 1 gets a second chance
(bit cleared, hand advances); the first page with bit 0 is evicted.

Author: Sabina Gasimova
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .core import PageReplacementAlgorithm, register


@register("clock")
class Clock(PageReplacementAlgorithm):
    name = "Second Chance (Clock)"
    short_name = "CLOCK"

    def reset(self, references, frame_count) -> None:
        self.frame_count = frame_count
        self.hand = 0
        self.ref_bit: Dict[int, int] = {}

    def on_hit(self, page: int, time: int) -> None:
        self.ref_bit[page] = 1

    def on_load(self, page: int, time: int, slot: int) -> None:
        self.ref_bit[page] = 1
        self.hand = (slot + 1) % self.frame_count

    def on_evict(self, page: int) -> None:
        self.ref_bit.pop(page, None)

    def choose_victim(self, time: int, slots: List[Optional[int]]) -> int:
        # Terminates in at most two sweeps: the first sweep clears every bit.
        while True:
            page = slots[self.hand]
            if self.ref_bit[page]:
                self.ref_bit[page] = 0          # second chance
                self.hand = (self.hand + 1) % self.frame_count
            else:
                return page

    def describe(self, slots) -> str:
        bits = " ".join(
            f"{'>' if i == self.hand else ''}{p}:{self.ref_bit[p]}"
            for i, p in enumerate(slots) if p is not None
        )
        return f"el={self.hand}  bitler: {bits}"
