"""Aging page replacement (software approximation of LRU).

Every resident page has a reference bit R and an 8-bit counter. On every
clock tick (every `period` references) each counter is shifted right by one
and R is copied into the most significant bit, then R is cleared. The counter
therefore keeps a short, decaying history of recent use. On a fault the page
with the smallest (R, counter) is evicted; ties go to the page loaded first.

Compared with Clock (one bit of history), Aging distinguishes "used 1 tick
ago" from "used 5 ticks ago"; compared with LRU it needs no ordering update
on every access, only a periodic shift.

Author: Sabina Gasimova
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .core import PageReplacementAlgorithm, register


@register("aging")
class Aging(PageReplacementAlgorithm):
    name = "Aging (8 bit)"
    short_name = "AGING"

    def __init__(self, bits: int = 8, period: int = 2) -> None:
        if bits < 1 or period < 1:
            raise ValueError("bits ve period en az 1 olmalıdır")
        self.bits = bits
        self.period = period

    def reset(self, references, frame_count) -> None:
        self.counter: Dict[int, int] = {}
        self.r_bit: Dict[int, int] = {}
        self.loaded_at: Dict[int, int] = {}

    def on_hit(self, page: int, time: int) -> None:
        self.r_bit[page] = 1

    def on_load(self, page: int, time: int, slot: int) -> None:
        self.counter[page] = 0
        self.r_bit[page] = 1
        self.loaded_at[page] = time

    def on_evict(self, page: int) -> None:
        for d in (self.counter, self.r_bit, self.loaded_at):
            d.pop(page, None)

    def on_reference(self, page: int, time: int) -> None:
        if (time + 1) % self.period == 0:          # clock tick
            top = 1 << (self.bits - 1)
            for p in self.counter:
                self.counter[p] = (self.counter[p] >> 1) | (top if self.r_bit[p] else 0)
                self.r_bit[p] = 0

    def choose_victim(self, time: int, slots: List[Optional[int]]) -> int:
        return min(self.counter, key=lambda p: (self.r_bit[p], self.counter[p], self.loaded_at[p]))

    def describe(self, slots) -> str:
        w = self.bits
        return "R|sayaç: " + " ".join(
            f"{p}:{self.r_bit[p]}|{self.counter[p]:0{w}b}" for p in slots if p is not None)
