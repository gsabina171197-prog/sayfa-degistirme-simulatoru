"""Sayfa Değiştirme Algoritmaları Simülatörü - BİM 361 İşletim Sistemleri."""
from .core import (  # noqa: F401
    PageReplacementAlgorithm, SimulationError, SimulationResult, Step,
    available_algorithms, create, run_all, validate_input,
)


__version__ = "0.8.0"
