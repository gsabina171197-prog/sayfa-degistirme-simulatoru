"""Reading, parsing and generating reference strings.

Accepted file format: page numbers separated by spaces, commas, semicolons or
new lines. Everything after '#' on a line is a comment.

Author: Sabina Gasimova
"""
from __future__ import annotations

import random
import re
from pathlib import Path
from typing import List, Optional

from .core import SimulationError

_SEPARATORS = re.compile(r"[\s,;]+")


def parse_references(text: str, source: str = "girdi") -> List[int]:
    tokens: List[str] = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            tokens.extend(t for t in _SEPARATORS.split(line) if t)
    if not tokens:
        raise SimulationError(f"{source}: referans dizisi boş.")
    refs: List[int] = []
    for pos, tok in enumerate(tokens, start=1):
        try:
            value = int(tok)
        except ValueError:
            raise SimulationError(
                f"{source}: {pos}. değer '{tok}' bir tam sayı değil."
            ) from None
        if value < 0:
            raise SimulationError(f"{source}: {pos}. değer negatif ({value}).")
        refs.append(value)
    return refs


def read_reference_file(path: str) -> List[int]:
    p = Path(path)
    if not p.exists():
        raise SimulationError(f"Dosya bulunamadı: {path}")
    if not p.is_file():
        raise SimulationError(f"Bir dosya değil: {path}")
    try:
        text = p.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise SimulationError(f"Dosya UTF-8 metin olarak okunamadı: {path}") from None
    return parse_references(text, source=p.name)


# ---- reproducible workload generators --------------------------------------
WORKLOADS = ("uniform", "locality", "loop", "mixed")
WORKLOAD_TR = {
    "uniform": "Düzgün rastgele",
    "locality": "Yerellik (working set)",
    "loop": "Döngüsel tarama",
    "mixed": "Karma",
}


def generate(kind: str, length: int, pages: int, seed: Optional[int] = None) -> List[int]:
    """Generate a reference string. Same seed -> same string (reproducible)."""
    if length < 1:
        raise SimulationError("Uzunluk en az 1 olmalıdır.")
    if pages < 1:
        raise SimulationError("Sayfa sayısı en az 1 olmalıdır.")
    rng = random.Random(seed)

    if kind == "uniform":
        return [rng.randrange(pages) for _ in range(length)]

    if kind == "locality":
        # A small working set that slowly drifts through the address space;
        # 90% of references stay inside the current working set.
        ws = max(2, pages // 3)
        base, out = 0, []
        for i in range(length):
            if i and i % max(10, length // 8) == 0:
                base = (base + rng.randint(1, ws)) % pages
            if rng.random() < 0.9:
                out.append((base + rng.randrange(ws)) % pages)
            else:
                out.append(rng.randrange(pages))
        return out

    if kind == "loop":
        # Sequential scan of a loop (classic worst case for LRU/FIFO).
        span = max(2, pages)
        return [i % span for i in range(length)]

    if kind == "mixed":
        out: List[int] = []
        parts = ["locality", "loop", "uniform"]
        chunk = max(1, length // len(parts))
        for i, part in enumerate(parts):
            n = chunk if i < len(parts) - 1 else length - len(out)
            out.extend(generate(part, n, pages, rng.randrange(1 << 30)))
        return out[:length]

    raise SimulationError(f"Bilinmeyen iş yükü: {kind}. Seçenekler: {', '.join(WORKLOADS)}")
