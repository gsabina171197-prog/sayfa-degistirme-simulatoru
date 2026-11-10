"""Console rendering. Every function returns a string, so the same text can be
printed to the terminal (with colour) and written to the log file (without).

Author: Sabina Gasimova
"""
from __future__ import annotations

import os
import re
import sys
from typing import Dict, List, Sequence

from .analysis import Anomaly, WorkloadReport
from .core import SimulationResult
from .input_io import WORKLOAD_TR

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


class Style:
    enabled = True

    @classmethod
    def setup(cls, enabled: bool) -> None:
        cls.enabled = enabled and sys.stdout.isatty() and not os.environ.get("NO_COLOR")
        if cls.enabled and os.name == "nt":
            os.system("")  # enables ANSI escape codes on Windows 10+ terminals

    @classmethod
    def _c(cls, code: str, text: str) -> str:
        return f"\x1b[{code}m{text}\x1b[0m" if cls.enabled else text

    green = classmethod(lambda c, t: c._c("32", t))
    red = classmethod(lambda c, t: c._c("31", t))
    yellow = classmethod(lambda c, t: c._c("33", t))
    cyan = classmethod(lambda c, t: c._c("36", t))
    bold = classmethod(lambda c, t: c._c("1", t))
    dim = classmethod(lambda c, t: c._c("2", t))


def strip_ansi(text: str) -> str:
    return _ANSI.sub("", text)


def _vlen(text: str) -> int:
    return len(strip_ansi(text))


def _pad(text: str, width: int, right: bool = False) -> str:
    gap = " " * max(0, width - _vlen(text))
    return gap + text if right else text + gap


def table(headers: Sequence[str], rows: Sequence[Sequence[str]],
          right_cols: Sequence[int] = ()) -> str:
    widths = [_vlen(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], _vlen(cell))
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    def line(cells):
        return "| " + " | ".join(_pad(c, widths[i], i in right_cols)
                                  for i, c in enumerate(cells)) + " |"
    out = [sep, line([Style.bold(h) for h in headers]), sep.replace("-", "=")]
    out += [line(r) for r in rows]
    out.append(sep)
    return "\n".join(out)


def title(text: str) -> str:
    bar = "═" * (len(text) + 4)
    return Style.cyan(f"╔{bar}╗\n║  {Style.bold(text)}{Style.cyan('  ║')}\n╚{bar}╝")


def pct(x: float) -> str:
    return f"%{100 * x:.1f}".replace(".", ",")


def refs_line(refs: Sequence[int]) -> str:
    return " ".join(map(str, refs))


# ---- single algorithm --------------------------------------------------------
def step_table(result: SimulationResult, notes: bool = True) -> str:
    n = result.frame_count
    headers = ["Adım", "Sayfa"] + [f"Ç{i}" for i in range(n)] + ["Sonuç", "Çıkan"]
    if notes:
        headers.append("Algoritma durumu")
    rows = []
    for s in result.steps:
        frames = []
        for slot, p in enumerate(s.frames):
            cell = "-" if p is None else str(p)
            if slot == s.loaded_into:
                cell = Style.yellow(cell + "*")
            frames.append(cell)
        outcome = Style.green("HIT") if s.hit else Style.red("MISS")
        evicted = "" if s.evicted is None else str(s.evicted)
        row = [str(s.index), str(s.page)] + frames + [outcome, evicted]
        if notes:
            row.append(Style.dim(s.note))
        rows.append(row)
    return table(headers, rows, right_cols=(0, 1))


def grid(result: SimulationResult) -> str:
    """Classic textbook view: columns are references, rows are frames."""
    w = max(2, max(len(str(p)) for p in result.references))
    cell = lambda t: t.rjust(w)
    lines = ["Ref : " + " ".join(cell(str(p)) for p in result.references)]
    lines.append("      " + " ".join("-" * w for _ in result.references))
    for slot in range(result.frame_count):
        parts = []
        for s in result.steps:
            p = s.frames[slot]
            txt = cell("." if p is None else str(p))
            parts.append(Style.yellow(txt) if slot == s.loaded_into else txt)
        lines.append(f"Ç{slot:<3}: " + " ".join(parts))
    marks = [Style.red(cell("F")) if not s.hit else Style.green(cell("·")) for s in result.steps]
    lines.append("Hata: " + " ".join(marks) + Style.dim("   (F = sayfa hatası)"))
    return "\n".join(lines)


def summary_line(result: SimulationResult) -> str:
    return (f"{Style.bold(result.short_name)}: toplam erişim {result.total}, "
            f"sayfa hatası {Style.red(str(result.faults))}, isabet {Style.green(str(result.hits))}, "
            f"isabet oranı {pct(result.hit_ratio)}")


def algorithm_report(result: SimulationResult, notes: bool = True) -> str:
    head = title(f"{result.algorithm} ({result.short_name}) — {result.frame_count} çerçeve")
    return "\n".join([head, step_table(result, notes), "", grid(result), "", summary_line(result)])


# ---- comparison ----------------------------------------------------------------
def comparison(results: List[SimulationResult]) -> str:
    best = min(r.faults for r in results)
    opt = next((r.faults for r in results if r.short_name == "OPT"), None)
    rows = []
    for r in sorted(results, key=lambda r: (r.faults, r.short_name)):
        gap = "" if opt is None else (f"+{r.faults - opt}" if r.faults > opt else "0")
        name = Style.green(r.short_name + " ★") if r.faults == best else r.short_name
        rows.append([name, str(r.total), str(r.faults), str(r.hits),
                     pct(r.hit_ratio), pct(r.fault_ratio), gap])
    head = ["Algoritma", "Toplam Erişim", "Sayfa Hatası", "İsabet",
            "İsabet Oranı", "Hata Oranı", "OPT'a fark"]
    return table(head, rows, right_cols=(1, 2, 3, 4, 5, 6))


def bar_chart(results: List[SimulationResult], width: int = 40) -> str:
    worst = max(r.faults for r in results) or 1
    out = []
    for r in results:
        n = round(width * r.faults / worst)
        out.append(f"{r.short_name:<6} {Style.red('█' * n)}{'' if n else '▏'} {r.faults}")
    return "\n".join(out)


def pick_columns(table_: Dict[str, List[int]], lo: int, columns: Sequence[int]) -> Dict[str, List[int]]:
    hi = lo + len(next(iter(table_.values()))) - 1
    keep = [k for k in columns if lo <= k <= hi]
    return {a: [v[k - lo] for k in keep] for a, v in table_.items()}


def range_table(table_: Dict[str, List[int]], lo: int, columns: Sequence[int] = ()) -> str:
    hi = lo + len(next(iter(table_.values()))) - 1
    cols = list(columns) or list(range(lo, hi + 1))
    headers = ["Algoritma"] + [f"{k} çerçeve" for k in cols]
    rows = []
    for name, faults in table_.items():
        cells = [name]
        for i, f in enumerate(faults):
            txt = str(f)
            if i and f > faults[i - 1]:
                txt = Style.red(f"{f} ▲")
            cells.append(txt)
        rows.append(cells)
    return table(headers, rows, right_cols=tuple(range(1, len(headers))))


def anomalies(found: List[Anomaly], limit: int = 6) -> str:
    if not found:
        return Style.green("✓ Belady anomalisi tespit edilmedi.")
    lines = [Style.red(Style.bold("⚠ Belady anomalisi tespit edildi:"))]
    for a in found[:limit]:
        lines.append(f"  • {a.algorithm}: {a.frames_before} çerçeve → {a.faults_before} hata, "
                     f"{a.frames_after} çerçeve → {a.faults_after} hata "
                     f"(çerçeve arttı, hata {a.faults_after - a.faults_before} arttı)")
    if len(found) > limit:
        lines.append(Style.dim(f"  … ve {len(found) - limit} durum daha (CSV / grafikte tamamı)"))
    return "\n".join(lines)


def experiment_summary(rows, lo: int) -> str:
    """rows: (label, n_refs, n_pages, table, anomalies)."""
    algos = list(rows[0][3])
    headers = ["Program", "Referans", "Sayfa"] + [f"{a} ort." for a in algos] + ["Belady"]
    out = []
    for label, n, pages, tbl, found in rows:
        avg = {a: sum(v) / len(v) for a, v in tbl.items()}
        best = min(avg[a] for a in algos if a != "OPT") if len(algos) > 1 else None
        cells = [label, str(n), str(pages)]
        for a in algos:
            txt = f"{avg[a]:.0f}"
            if a != "OPT" and avg[a] == best:
                txt = Style.green(txt + " ★")
            cells.append(txt)
        cells.append(", ".join(sorted({x.algorithm for x in found})) or "—")
        out.append(cells)
    return "\n".join([
        table(headers, out, right_cols=tuple(range(1, len(headers) - 1))),
        Style.dim("Ortalama = çerçeve aralığı boyunca ortalama sayfa hatası; ★ = OPT hariç en iyi"),
    ])


def workload_summary(reports: List[WorkloadReport]) -> str:
    algos = list(reports[0].table)
    headers = ["İş yükü"] + [f"{a} ort. hata" for a in algos]
    rows = []
    for rep in reports:
        ratios = rep.average_fault_ratio()
        best = min(ratios[a] for a in algos if a != "OPT")
        cells = [WORKLOAD_TR.get(rep.workload, rep.workload)]
        for a in algos:
            txt = pct(ratios[a])
            if a != "OPT" and ratios[a] == best:
                txt = Style.green(txt + " ★")
            cells.append(txt)
        rows.append(cells)
    gap_rows = []
    for rep in reports:
        gaps = rep.gap_to_optimal()
        gap_rows.append([WORKLOAD_TR.get(rep.workload, rep.workload)] +
                        [f"+{gaps[a]:.1f}%".replace(".", ",") for a in algos])
    return "\n".join([
        table(headers, rows, right_cols=tuple(range(1, len(headers)))),
        "",
        Style.bold("OPT'a göre ortalama fazladan hata (düşük = iyi):"),
        table(["İş yükü"] + algos, gap_rows, right_cols=tuple(range(1, len(algos) + 1))),
        Style.dim("★ = gerçekte uygulanabilir algoritmalar içinde en iyisi (OPT hariç)"),
    ])
