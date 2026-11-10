#!/usr/bin/env python3
"""Sayfa Değiştirme Algoritmaları Simülatörü — komut satırı arayüzü.

Örnekler:
  python main.py --file data/ornek.txt --frames 3
  python main.py --file data/ornek.txt --frames 3 --step
  python main.py --file data/belady.txt --range 1 6
  python main.py --random 30 --pages 8 --seed 361 --frames 4
  python main.py --workloads --range 2 10
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from simulator import SimulationError, __version__, available_algorithms, create, run_all
from simulator import analysis, display, export, html_report
from simulator.display import Style
from simulator.input_io import WORKLOADS, generate, parse_references, read_reference_file
from simulator import trace as tr


LONG_INPUT = 500                            # beyond this: summary only, no step tables
EXPERIMENT_COLUMNS = [1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 32, 40]


class Output:
    """Prints to the console and keeps an ANSI-free copy for the log file."""

    def __init__(self) -> None:
        self.buffer: List[str] = []

    def __call__(self, text: str = "") -> None:
        print(text)
        self.buffer.append(display.strip_ansi(text))

    def text(self) -> str:
        return "\n".join(self.buffer)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="main.py",
        description="FIFO, LRU, Optimal, Clock, LFU ve Aging sayfa değiştirme "
                    "algoritmalarını aynı girdide adım adım karşılaştırır.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Örnekler:" + __doc__.split("Örnekler:", 1)[1],
    )
    src = p.add_argument_group("girdi (birini seçin)")
    g = src.add_mutually_exclusive_group()
    g.add_argument("--file", "-f", help="referans dizisini içeren metin dosyası")
    g.add_argument("--refs", "-r", help='referans dizisi, ör. "7 0 1 2 0 3"')
    g.add_argument("--random", type=int, metavar="N", help="N uzunlukta rastgele dizi üret")
    g.add_argument("--workloads", action="store_true",
                   help="farklı iş yükü türlerinde performans analizi (rastgele, yerellik, döngü, karma)")
    g.add_argument("--trace", "-t", metavar="DOSYA",
                   help="bellek erişim izi (Valgrind Lackey biçimi veya satır başına bir adres)")
    g.add_argument("--program", choices=list(tr.PROGRAMS),
                   help="izlenen gerçek bir programın (matris, quicksort, ikili arama) erişim izi")
    g.add_argument("--experiment", action="store_true",
                   help="tüm izlenen programlarda deney: çerçeve aralığı, Belady, grafikler")
    src.add_argument("--page-size", type=int, default=None,
                     help="iz için sayfa boyutu, bayt (vars. --trace 4096, --program 512)")
    src.add_argument("--no-collapse", action="store_true",
                     help="izde aynı sayfaya art arda erişimleri tek erişime indirme")
    src.add_argument("--pages", type=int, default=8, help="rastgele dizide farklı sayfa sayısı (vars. 8)")
    src.add_argument("--seed", type=int, default=361, help="tohum değeri — aynı tohum aynı dizi (vars. 361)")
    src.add_argument("--length", type=int, default=200, help="--workloads için dizi uzunluğu (vars. 200)")
    src.add_argument("--save-refs", metavar="DOSYA", help="kullanılan referans dizisini dosyaya kaydet")

    mode = p.add_argument_group("çalıştırma")
    mode.add_argument("--frames", "-k", type=int, help="bellek çerçevesi sayısı")
    mode.add_argument("--range", nargs=2, type=int, metavar=("MIN", "MAX"),
                      help="çerçeve aralığında hata analizi + Belady anomalisi tespiti")
    mode.add_argument("--algo", "-a", nargs="+", choices=available_algorithms(),
                      help="çalıştırılacak algoritmalar (vars. hepsi)")
    mode.add_argument("--step", action="store_true",
                      help="canlı demo: her erişimde Enter ile ilerle, tüm algoritmalar yan yana")

    out = p.add_argument_group("çıktı")
    out.add_argument("--out", "-o", default="results", help="çıktı klasörü (vars. results/)")
    out.add_argument("--no-export", action="store_true", help="dosyaya çıktı yazma")
    out.add_argument("--summary", "-s", action="store_true", help="adım tablolarını gösterme, sadece özet")
    out.add_argument("--no-notes", action="store_true", help="adım tablosunda algoritma durum sütununu gizle")
    out.add_argument("--no-color", action="store_true", help="renkli çıktıyı kapat")
    out.add_argument("--open", action="store_true", help="HTML raporu tarayıcıda aç")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def load_references(args) -> List[int]:
    if args.file:
        return read_reference_file(args.file)
    if args.refs:
        return parse_references(args.refs, source="--refs")
    if args.random is not None:
        return generate("uniform", args.random, args.pages, args.seed)
    if args.trace or args.program:
        t = (tr.read_trace(args.trace, args.page_size or 4096) if args.trace
             else tr.program_trace(args.program, args.page_size or 512))
        refs = t.renumbered(collapse=not args.no_collapse)
        print(Style.dim(f"İz: {t.name} — {len(t.addresses)} bellek erişimi, sayfa boyutu {t.page_size} B → "
                        f"{len(refs)} sayfa referansı ({'art arda tekrarlar birleştirildi' if not args.no_collapse else 'birleştirme yok'})"))
        return refs
    raise SimulationError("Girdi verilmedi: --file, --refs, --random veya --workloads kullanın.")


# ---- modes -----------------------------------------------------------------
def run_single(refs, args, out: Output) -> None:
    long_input = len(refs) > LONG_INPUT
    if long_input and not args.summary:
        out(Style.yellow(f"Dizi uzun ({len(refs)} erişim): adım tabloları ve HTML rapor atlanıyor, özet gösteriliyor."))
        args.summary = True
    results = run_all(refs, args.frames, args.algo, record=not long_input)
    if not args.summary:
        for r in results:
            out(display.algorithm_report(r, notes=not args.no_notes))
            out()
    out(display.title(f"Karşılaştırma — {args.frames} çerçeve, {len(refs)} erişim"))
    out(display.comparison(results))
    out()
    out(Style.bold("Sayfa hatası sayısı:"))
    out(display.bar_chart(results))
    if not args.no_export and long_input:
        paths = [export.write_summary_csv(results, args.out)]
        out()
        out(Style.dim("Dosyalar: " + ", ".join(str(p) for p in paths)))
    elif not args.no_export:
        hi = max(args.frames, min(len(set(refs)), 10))
        table = analysis.frame_range(refs, 1, hi, args.algo)
        report = html_report.build(results, table, 1, analysis.detect_belady(table, 1),
                                   source=args.file or ("--refs" if args.refs else f"rastgele (tohum {args.seed})"))
        paths = [export.write_steps_csv(results, args.out),
                 export.write_summary_csv(results, args.out),
                 export.write_json(args.out, export.results_payload(results)),
                 html_report.write(report, args.out)]
        if args.open:
            import webbrowser
            webbrowser.open(paths[-1].resolve().as_uri())
        out()
        out(Style.dim("Dosyalar: " + ", ".join(str(p) for p in paths)))


def run_range(refs, args, out: Output) -> None:
    lo, hi = args.range
    table = analysis.frame_range(refs, lo, hi, args.algo)
    found = analysis.detect_belady(table, lo)
    out(display.title(f"Çerçeve Aralığı Analizi — {lo}..{hi} çerçeve, {len(refs)} erişim"))
    out(display.range_table(table, lo))
    out()
    out(display.anomalies(found))
    if "OPT" in table:
        ok = analysis.optimal_is_lower_bound(table)
        out(Style.green("✓ Optimal her çerçeve sayısında alt sınır.") if ok
            else Style.red("✗ Optimal alt sınır değil — hata!"))
    if not args.no_export:
        svg = export.svg_line_chart(table, lo, "Çerçeve sayısına göre sayfa hatası",
                                    f"Referans dizisi ({len(refs)} erişim): {display.refs_line(refs[:40])}"
                                    + (" …" if len(refs) > 40 else ""), found)
        paths = [export.write_range_csv(table, lo, args.out),
                 export.write_svg(svg, args.out, "grafik_cerceve_hata.svg")]
        out()
        out(Style.dim("Dosyalar: " + ", ".join(str(p) for p in paths)))


def run_experiment(args, out: Output) -> None:
    lo, hi = args.range or (1, 40)
    size = args.page_size or 512
    out(display.title(f"Deney: izlenen programlar — sayfa {size} B, {lo}..{hi} çerçeve"))
    rows, all_tables = [], {}
    for key, (label, _) in tr.PROGRAMS.items():
        t = tr.program_trace(key, size)
        refs = t.renumbered(collapse=not args.no_collapse)
        table = analysis.frame_range(refs, lo, hi, args.algo)
        found = analysis.detect_belady(table, lo)
        all_tables[key] = (label, t, refs, table, found)
        out()
        out(Style.bold(f"▸ {label}") + Style.dim(
            f"  {len(t.addresses)} erişim → {len(refs)} sayfa referansı, {len(set(refs))} farklı sayfa"))
        out(display.range_table(display.pick_columns(table, lo, EXPERIMENT_COLUMNS), lo,
                                columns=[k for k in EXPERIMENT_COLUMNS if lo <= k <= hi]))
        out(display.anomalies(found) if found else Style.green("✓ Belady anomalisi yok."))
        rows.append((label, len(refs), len(set(refs)), table, found))
    out()
    out(display.title("Özet"))
    out(display.experiment_summary(rows, lo))
    if not args.no_export:
        paths = [export.write_experiment_csv(all_tables, lo, args.out)]
        for key, (label, t, refs, table, found) in all_tables.items():
            svg = export.svg_line_chart(table, lo, f"{label} — çerçeve sayısına göre sayfa hatası",
                                        f"{len(t.addresses)} bellek erişimi, sayfa {t.page_size} B, "
                                        f"{len(set(refs))} farklı sayfa", found)
            paths.append(export.write_svg(svg, args.out, f"deney_{key}.svg"))
        out()
        out(Style.dim("Dosyalar: " + ", ".join(str(p) for p in paths)))


def run_workloads(args, out: Output) -> None:
    lo, hi = args.range or (2, 10)
    reports = analysis.workload_analysis(args.length, args.pages,
                                         lo, hi, args.seed, WORKLOADS, args.algo)
    out(display.title(f"İş Yükü Performans Analizi — {args.length} erişim, {lo}..{hi} çerçeve, tohum {args.seed}"))
    for rep in reports:
        out()
        out(Style.bold(f"▸ {display.WORKLOAD_TR[rep.workload]}") +
            Style.dim(f"  ilk 20 erişim: {display.refs_line(rep.references[:20])} …"))
        out(display.range_table(rep.table, lo))
        found = analysis.detect_belady(rep.table, lo)
        if found:
            out(display.anomalies(found))
    out()
    out(display.title("Özet: ortalama sayfa hatası oranı"))
    out(display.workload_summary(reports))
    if not args.no_export:
        paths = [export.write_workload_csv(reports, args.out)] + export.workload_charts(reports, args.out)
        out()
        out(Style.dim("Dosyalar: " + ", ".join(str(p) for p in paths)))


def run_step(refs, args, out: Output) -> None:
    """Live demo: all algorithms advance together, one reference per Enter."""
    results = run_all(refs, args.frames, args.algo)
    out(display.title(f"Canlı adım adım simülasyon — {args.frames} çerçeve"))
    out(Style.dim("Enter: sonraki adım   a: sona kadar oynat   q: çık"))
    autoplay = False
    for i, page in enumerate(refs):
        out()
        rest = display.refs_line(refs[i + 1:])
        out(Style.bold(f"Adım {i + 1}/{len(refs)}  →  sayfa {page}") + Style.dim(f"   kalan: {rest}"))
        rows = []
        for r in results:
            s = r.steps[i]
            frames = " ".join(
                (Style.yellow(f"[{p}]") if slot == s.loaded_into else f"[{p}]") if p is not None else "[ ]"
                for slot, p in enumerate(s.frames))
            faults_so_far = sum(1 for x in r.steps[: i + 1] if not x.hit)
            rows.append([r.short_name, frames, Style.green("HIT") if s.hit else Style.red("MISS"),
                         "" if s.evicted is None else str(s.evicted), str(faults_so_far),
                         Style.dim(s.note)])
        out(display.table(["Alg.", "Çerçeveler", "Sonuç", "Çıkan", "Σ hata", "Neden / durum"], rows,
                          right_cols=(4,)))
        if not autoplay and i < len(refs) - 1:
            try:
                key = input(Style.dim("» ")).strip().lower()
            except EOFError:
                key = "a"
            if key == "q":
                out("Demo durduruldu.")
                return
            autoplay = key == "a"
    out()
    out(display.comparison(results))


MENU = [
    ("Örnek senaryo — 6 algoritma, adım tabloları, karşılaştırma, HTML rapor",
     ["--file", "data/ornek.txt", "--frames", "3", "--open"]),
    ("Canlı adım adım demo (Enter ile ilerle)", ["--file", "data/ornek.txt", "--frames", "3", "--step"]),
    ("Belady anomalisi — çerçeve aralığı analizi", ["--file", "data/belady.txt", "--range", "1", "6"]),
    ("İş yükü performans analizi", ["--workloads", "--range", "2", "8", "--summary"]),
    ("Algoritma erişim izleri deneyi (matris, quicksort, ikili arama)", ["--experiment"]),
    ("Valgrind izi okuma örneği", ["--trace", "data/izler/matris_carpim_8.lackey", "--page-size", "256", "--range", "1", "8"]),
    ("Hatalı girdi kontrolü", ["--file", "data/hatali_ornek.txt", "--frames", "3"]),
]


def interactive_menu() -> int:
    """Shown when main.py is started without arguments (double-click friendly)."""
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # data/ paths work from anywhere
    Style.setup(True)
    while True:
        print()
        print(display.title("Sayfa Değiştirme Algoritmaları Simülatörü"))
        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {i}) {label}")
        print(f"  {len(MENU) + 1}) Kendi referans dizimi gireceğim")
        print("  0) Çıkış")
        try:
            choice = input(Style.dim("Seçim » ")).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if choice == "0":
            return 0
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            main(MENU[int(choice) - 1][1])
        elif choice == str(len(MENU) + 1):
            try:
                refs = input("Referans dizisi (ör. 7 0 1 2 0 3): ").strip()
                frames = input("Çerçeve sayısı: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                continue
            main(["--refs", refs, "--frames", frames])
        else:
            print(Style.red("Geçersiz seçim."))


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # Windows code pages: never crash on ═ ✓ ★ etc.
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:  # argparse already printed the message
        return int(exc.code or 0)
    Style.setup(not args.no_color)
    out = Output()
    try:
        if args.workloads:
            run_workloads(args, out)
        elif args.experiment:
            run_experiment(args, out)
        else:
            refs = load_references(args)
            if args.save_refs:
                with open(args.save_refs, "w", encoding="utf-8") as f:
                    f.write(" ".join(map(str, refs)) + "\n")
            if args.range is None and args.frames is None:
                raise SimulationError("--frames veya --range belirtilmelidir.")
            out(Style.dim(f"Referans dizisi ({len(refs)} erişim, {len(set(refs))} farklı sayfa): ")
                + display.refs_line(refs[:60]) + (" …" if len(refs) > 60 else ""))
            out()
            if args.range is not None:
                run_range(refs, args, out)
                if args.frames is not None:
                    out()
            if args.frames is not None:
                (run_step if args.step else run_single)(refs, args, out)
    except SimulationError as exc:
        print(Style.red(f"Hata: {exc}"), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nİptal edildi.", file=sys.stderr)
        return 130
    if not args.no_export:
        export.write_log(out.text(), args.out)
    return 0


if __name__ == "__main__":
    sys.exit(interactive_menu() if len(sys.argv) == 1 else main())
