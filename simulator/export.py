"""Writing results to files: CSV, JSON, SVG chart and the plain-text run log.
Standard library only (csv, json, xml.sax.saxutils).

Author: Sabina Gasimova
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence
from xml.sax.saxutils import escape

from .analysis import Anomaly, WorkloadReport
from .core import SimulationResult
from .input_io import WORKLOAD_TR

# Fixed colour per algorithm (colour follows the entity, never its rank),
# plus a dash pattern and marker shape so identity never relies on colour alone.
SERIES = {
    "FIFO":  ("#2a78d6", "",      "circle"),
    "LRU":   ("#eb6834", "6 4",   "square"),
    "OPT":   ("#1baf7a", "",      "diamond"),
    "CLOCK": ("#c98500", "2 3",   "triangle"),
    "LFU":   ("#d55181", "8 3 2 3", "circle-open"),
}


def _dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_steps_csv(results: List[SimulationResult], out_dir: str) -> Path:
    path = _dir(out_dir) / "adimlar.csv"
    width = max(r.frame_count for r in results)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["algoritma", "adim", "sayfa"] + [f"cerceve_{i}" for i in range(width)]
                   + ["sonuc", "cikarilan", "aciklama"])
        for r in results:
            for s in r.steps:
                frames = ["" if p is None else p for p in s.frames]
                frames += [""] * (width - len(frames))
                w.writerow([r.short_name, s.index, s.page] + frames +
                           ["HIT" if s.hit else "MISS",
                            "" if s.evicted is None else s.evicted, s.note])
    return path


def write_summary_csv(results: List[SimulationResult], out_dir: str) -> Path:
    path = _dir(out_dir) / "ozet.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        rows = [r.summary() for r in results]
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";")
        w.writeheader()
        w.writerows(rows)
    return path


def write_range_csv(table: Dict[str, List[int]], lo: int, out_dir: str,
                    name: str = "cerceve_analizi.csv") -> Path:
    path = _dir(out_dir) / name
    n = len(next(iter(table.values())))
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["cerceve"] + list(table))
        for i in range(n):
            w.writerow([lo + i] + [table[a][i] for a in table])
    return path


def write_workload_csv(reports: List[WorkloadReport], out_dir: str) -> Path:
    path = _dir(out_dir) / "is_yuku_analizi.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["is_yuku", "cerceve", "algoritma", "sayfa_hatasi", "hata_orani"])
        for rep in reports:
            n = len(rep.references)
            for algo, faults in rep.table.items():
                for i, x in enumerate(faults):
                    w.writerow([rep.workload, rep.lo + i, algo, x, round(x / n, 4)])
    return path


def write_json(path_dir: str, payload: dict, name: str = "sonuclar.json") -> Path:
    path = _dir(path_dir) / name
    payload = {"olusturulma": datetime.now().isoformat(timespec="seconds"), **payload}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def results_payload(results: List[SimulationResult]) -> dict:
    return {
        "referans_dizisi": list(results[0].references),
        "cerceve_sayisi": results[0].frame_count,
        "algoritmalar": [
            {**r.summary(),
             "adimlar": [{"adim": s.index, "sayfa": s.page, "cerceveler": list(s.frames),
                          "isabet": s.hit, "cikarilan": s.evicted, "aciklama": s.note}
                         for s in r.steps]}
            for r in results
        ],
    }


def write_log(text: str, out_dir: str, name: str = "calisma_logu.txt") -> Path:
    path = _dir(out_dir) / name
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n===== Çalıştırma: {stamp} =====\n{text}\n")
    return path


# ---- SVG line chart -------------------------------------------------------
def _marker(shape: str, x: float, y: float, color: str) -> str:
    r = 4.5
    if shape == "square":
        return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" rx="1" fill="{color}"/>'
    if shape == "diamond":
        return (f'<path d="M{x:.1f} {y - r - 1:.1f} L{x + r + 1:.1f} {y:.1f} L{x:.1f} {y + r + 1:.1f} '
                f'L{x - r - 1:.1f} {y:.1f}Z" fill="{color}"/>')
    if shape == "triangle":
        return (f'<path d="M{x:.1f} {y - r - 1:.1f} L{x + r + 1:.1f} {y + r:.1f} '
                f'L{x - r - 1:.1f} {y + r:.1f}Z" fill="{color}"/>')
    if shape == "circle-open":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r - 0.5}" fill="#fcfcfb" stroke="{color}" stroke-width="2"/>'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"/>'


def svg_line_chart(table: Dict[str, List[int]], lo: int, chart_title: str,
                   subtitle: str = "", anomalies: Sequence[Anomaly] = (),
                   y_label: str = "Sayfa hatası") -> str:
    W, H = 760, 440
    L, R, T, B = 64, 36, 112, 58
    pw, ph = W - L - R, H - T - B
    n = len(next(iter(table.values())))
    xs = list(range(lo, lo + n))
    y_max = max(max(v) for v in table.values())
    step = 1 if y_max <= 10 else 2 if y_max <= 20 else 5 if y_max <= 50 else 10 if y_max <= 100 else 50
    y_top = ((y_max // step) + 1) * step

    def X(k: int) -> float:
        return L + (pw * (k - lo) / (n - 1) if n > 1 else pw / 2)

    def Y(v: float) -> float:
        return T + ph * (1 - v / y_top)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fcfcfb"/>',
         f'<text x="{L}" y="30" font-size="17" font-weight="600" fill="#0b0b0b">{escape(chart_title)}</text>']
    if subtitle:
        o.append(f'<text x="{L}" y="50" font-size="12" fill="#52514e">{escape(subtitle)}</text>')
    # grid + y axis
    for v in range(0, y_top + 1, step):
        y = Y(v)
        o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{L + pw}" y2="{y:.1f}" stroke="#e4e3df" stroke-width="1"/>')
        o.append(f'<text x="{L - 8}" y="{y + 4:.1f}" font-size="11" fill="#52514e" text-anchor="end">{v}</text>')
    for k in xs:
        o.append(f'<text x="{X(k):.1f}" y="{T + ph + 20}" font-size="11" fill="#52514e" text-anchor="middle">{k}</text>')
    o.append(f'<text x="{L + pw / 2}" y="{H - 14}" font-size="12" fill="#52514e" text-anchor="middle">Çerçeve sayısı</text>')
    o.append(f'<text transform="translate(18 {T + ph / 2}) rotate(-90)" font-size="12" fill="#52514e" '
             f'text-anchor="middle">{escape(y_label)}</text>')
    # anomaly bands
    for a in anomalies:
        x1, x2 = X(a.frames_before), X(a.frames_after)
        o.append(f'<rect x="{x1:.1f}" y="{T}" width="{x2 - x1:.1f}" height="{ph}" fill="#e34948" opacity="0.08">'
                 f'<title>Belady anomalisi ({escape(a.algorithm)}): {a.frames_before}→{a.frames_after} çerçeve, '
                 f'{a.faults_before}→{a.faults_after} hata</title></rect>')
        o.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{T - 6}" font-size="11" fill="#b42318" text-anchor="middle">'
                 f'Belady ({escape(a.algorithm)})</text>')
    # series
    for name, values in table.items():
        color, dash, shape = SERIES.get(name, ("#6250d6", "", "circle"))
        pts = " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in zip(xs, values))
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        o.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"'
                 f' stroke-linejoin="round"{dash_attr}/>')
        for k, v in zip(xs, values):
            o.append(f'<g><circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="11" fill="transparent">'
                     f'<title>{escape(name)} — {k} çerçeve: {v} hata</title></circle>'
                     f'{_marker(shape, X(k), Y(v), color)}</g>')
        # direct end labels only for <= 4 series; with more, the legend carries identity
        if len(table) <= 4:
            o.append(f'<text x="{X(xs[-1]) + 8:.1f}" y="{Y(values[-1]) + 4:.1f}" font-size="12" '
                     f'fill="#0b0b0b">{escape(name)}</text>')
    o.append(f'<line x1="{L}" y1="{T + ph}" x2="{L + pw}" y2="{T + ph}" stroke="#8a8984" stroke-width="1"/>')
    # legend (always present for >= 2 series)
    lx = L
    for name in table:
        color, dash, shape = SERIES.get(name, ("#6250d6", "", "circle"))
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        o.append(f'<line x1="{lx}" y1="{T - 44}" x2="{lx + 22}" y2="{T - 44}" stroke="{color}" stroke-width="2"{dash_attr}/>')
        o.append(_marker(shape, lx + 11, T - 44, color))
        o.append(f'<text x="{lx + 28}" y="{T - 40}" font-size="12" fill="#0b0b0b">{escape(name)}</text>')
        lx += 40 + 8 * len(name) + 18
    o.append("</svg>")
    return "\n".join(o)


def write_svg(svg: str, out_dir: str, name: str) -> Path:
    path = _dir(out_dir) / name
    path.write_text(svg, encoding="utf-8")
    return path


def workload_charts(reports: List[WorkloadReport], out_dir: str) -> List[Path]:
    paths = []
    for rep in reports:
        n = len(rep.references)
        svg = svg_line_chart(rep.table, rep.lo,
                             f"İş yükü: {WORKLOAD_TR.get(rep.workload, rep.workload)}",
                             f"{n} erişim, {len(set(rep.references))} farklı sayfa — çerçeve sayısına göre sayfa hatası")
        paths.append(write_svg(svg, out_dir, f"grafik_{rep.workload}.svg"))
    return paths
