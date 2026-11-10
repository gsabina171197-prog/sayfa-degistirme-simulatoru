"""Sayfa Değiştirme Algoritmaları Simülatörü - BİM 361 İşletim Sistemleri."""
from .core import (  # noqa: F401
    PageReplacementAlgorithm, SimulationError, SimulationResult, Step,
    available_algorithms, create, run_all, validate_input,
)
# Import order = default display order (registration happens on import).
from . import fifo, lru, optimal, clock  # noqa: F401,E402

__version__ = "0.8.0"
