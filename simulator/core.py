"""Shared data model and the common interface every algorithm implements.

Every algorithm receives the same input (reference string + frame count) and
returns the same output (step records + summary). The comparison, analysis,
display and export modules therefore never depend on a specific algorithm.

Author: Sabina Gasimova
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Type


class SimulationError(ValueError):
    """Raised for invalid simulation input (empty string, bad frame count...)."""


@dataclass(frozen=True)
class Step:
    """State of memory right after one page reference."""

    index: int                         # 1-based position in the reference string
    page: int                          # referenced page
    frames: Tuple[Optional[int], ...]  # frame contents by slot (None = empty)
    hit: bool                          # True = hit, False = page fault
    evicted: Optional[int]             # page removed from memory (if any)
    loaded_into: Optional[int]         # slot index the page was loaded into (miss only)
    note: str = ""                     # algorithm-specific explanation of the decision

    @property
    def fault(self) -> bool:
        return not self.hit


@dataclass
class SimulationResult:
    """Full result of one algorithm on one input."""

    algorithm: str
    short_name: str
    references: Tuple[int, ...]
    frame_count: int
    steps: List[Step] = field(default_factory=list)
    fault_count: Optional[int] = None   # set when steps are not recorded (fast mode)

    @property
    def total(self) -> int:
        return len(self.references)

    @property
    def faults(self) -> int:
        if self.fault_count is not None:
            return self.fault_count
        return sum(1 for s in self.steps if not s.hit)

    @property
    def hits(self) -> int:
        return self.total - self.faults

    @property
    def hit_ratio(self) -> float:
        return self.hits / self.total if self.total else 0.0

    @property
    def fault_ratio(self) -> float:
        return self.faults / self.total if self.total else 0.0

    @property
    def evictions(self) -> int:
        if not self.steps:
            return self.faults - min(self.frame_count, len(set(self.references)))
        return sum(1 for s in self.steps if s.evicted is not None)

    def summary(self) -> Dict[str, object]:
        return {
            "algoritma": self.short_name,
            "cerceve": self.frame_count,
            "toplam_erisim": self.total,
            "sayfa_hatasi": self.faults,
            "isabet": self.hits,
            "isabet_orani": round(self.hit_ratio, 4),
            "hata_orani": round(self.fault_ratio, 4),
            "cikarilan_sayfa": self.evictions,
        }


def validate_input(references: Sequence[int], frame_count: int) -> Tuple[int, ...]:
    """Validate and normalise the simulation input."""
    if isinstance(frame_count, bool) or not isinstance(frame_count, int):
        raise SimulationError("Çerçeve sayısı bir tam sayı olmalıdır.")
    if frame_count < 1:
        raise SimulationError("Çerçeve sayısı en az 1 olmalıdır.")
    refs = tuple(references)
    if not refs:
        raise SimulationError("Referans dizisi boş olamaz.")
    for value in refs:
        if isinstance(value, bool) or not isinstance(value, int):
            raise SimulationError(f"Geçersiz sayfa numarası: {value!r} (tam sayı olmalı).")
        if value < 0:
            raise SimulationError(f"Negatif sayfa numarası kullanılamaz: {value}.")
    return refs


class PageReplacementAlgorithm(ABC):
    """Template for all policies.

    The base class owns the frame table (slots) and the hit/miss bookkeeping.
    A concrete policy only answers: "which resident page should be evicted?"
    plus optional hooks to update its own data structure.
    """

    name: str = "Abstract"
    short_name: str = "ABS"

    # ---- hooks for subclasses -------------------------------------------
    def reset(self, references: Tuple[int, ...], frame_count: int) -> None:
        """Prepare internal state before a run."""

    def on_hit(self, page: int, time: int) -> None:
        """Called when `page` is referenced and already resident."""

    def on_load(self, page: int, time: int, slot: int) -> None:
        """Called after `page` was loaded into `slot`."""

    def on_evict(self, page: int) -> None:
        """Called after `page` was removed from memory."""

    def on_reference(self, page: int, time: int) -> None:
        """Called once per reference, after the hit/miss handling (e.g. a clock tick)."""

    @abstractmethod
    def choose_victim(self, time: int, slots: List[Optional[int]]) -> int:
        """Return the resident page to evict (memory is full)."""

    def describe(self, slots: List[Optional[int]]) -> str:
        """Short human-readable state of the policy's data structure."""
        return ""

    # ---- driver -----------------------------------------------------------
    def run(self, references: Sequence[int], frame_count: int,
            record: bool = True) -> SimulationResult:
        """Simulate. With record=False only the fault count is kept (fast mode for
        long traces and frame-range sweeps)."""
        refs = validate_input(references, frame_count)
        self.reset(refs, frame_count)
        slots: List[Optional[int]] = [None] * frame_count
        where: Dict[int, int] = {}  # page -> slot
        result = SimulationResult(self.name, self.short_name, refs, frame_count)
        faults = 0

        for time, page in enumerate(refs):
            evicted: Optional[int] = None
            loaded_into: Optional[int] = None
            if page in where:
                hit = True
                self.on_hit(page, time)
            else:
                hit = False
                faults += 1
                if len(where) < frame_count:
                    slot = slots.index(None)
                else:
                    evicted = self.choose_victim(time, slots)
                    if evicted not in where:
                        raise RuntimeError(f"{self.short_name}: geçersiz kurban {evicted}")
                    slot = where.pop(evicted)
                    self.on_evict(evicted)
                slots[slot] = page
                where[page] = slot
                loaded_into = slot
                self.on_load(page, time, slot)
            self.on_reference(page, time)
            if record:
                result.steps.append(
                    Step(time + 1, page, tuple(slots), hit, evicted, loaded_into, self.describe(slots))
                )
        if not record:
            result.fault_count = faults
        return result


# ---- registry ---------------------------------------------------------------
_REGISTRY: Dict[str, Type[PageReplacementAlgorithm]] = {}


def register(key: str):
    """Class decorator: makes an algorithm selectable from the CLI by `key`."""

    def wrap(cls: Type[PageReplacementAlgorithm]) -> Type[PageReplacementAlgorithm]:
        _REGISTRY[key] = cls
        return cls

    return wrap


def available_algorithms() -> List[str]:
    return list(_REGISTRY)


def create(key: str) -> PageReplacementAlgorithm:
    try:
        return _REGISTRY[key]()
    except KeyError:
        raise SimulationError(
            f"Bilinmeyen algoritma: {key}. Seçenekler: {', '.join(_REGISTRY)}"
        ) from None


def run_all(references: Sequence[int], frame_count: int,
            keys: Optional[Sequence[str]] = None, record: bool = True) -> List[SimulationResult]:
    """Run several algorithms on exactly the same input."""
    keys = list(keys) if keys else available_algorithms()
    return [create(k).run(references, frame_count, record) for k in keys]
