"""Self-contained interactive HTML report (no internet, no external files).

Contents: summary cards, comparison table, an animated step-by-step viewer
that replays all algorithms side by side, per-algorithm step tables, the
frame-count vs page-fault chart with Belady detection, and the run metadata.

Author: Sabina Gasimova
"""
from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Dict, List

from . import __version__
from .analysis import Anomaly, optimal_is_lower_bound
from .core import SimulationResult
from .export import SERIES, svg_line_chart

_CSS = """
:root{--bg:#f4f2ec;--card:#fff;--ink:#16181d;--muted:#5b5f66;--line:#dedbd2;--hit:#1a7f4b;--miss:#c4471a;--accent:#1f5fae}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 "Segoe UI",Inter,Helvetica,Arial,sans-serif}
main{max-width:1180px;margin:0 auto;padding:40px 24px 80px}
h1{font-size:34px;margin:0 0 4px}h2{font-size:24px;margin:48px 0 16px}h3{margin:0 0 8px}
.mono{font-family:"JetBrains Mono",Consolas,"Courier New",monospace}.muted{color:var(--muted)}
.refs{font-size:22px;letter-spacing:2px;color:var(--accent);font-weight:700;word-break:break-word}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin-top:24px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.card .big{font-size:34px;font-weight:700}.card .lbl{color:var(--muted);font-size:14px}
table{border-collapse:collapse;width:100%;background:var(--card);border-radius:12px;overflow:hidden}
th,td{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left}th{background:#ecebe5;font-weight:600}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.hit{color:var(--hit);font-weight:700}.miss{color:var(--miss);font-weight:700}
.best{background:#e7f4ec}
.viewer{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}
.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:16px}
button{font:inherit;padding:8px 14px;border-radius:10px;border:1px solid var(--line);background:#fff;cursor:pointer}
button.primary{background:var(--ink);color:#fff;border-color:var(--ink)}
input[type=range]{flex:1;min-width:200px}
.strip{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:16px}
.strip span{min-width:30px;text-align:center;padding:4px 0;border-radius:6px;background:#ecebe5;cursor:pointer}
.strip span.past{background:#d9d6cc}.strip span.now{background:var(--accent);color:#fff;font-weight:700}
.frame{display:inline-block;min-width:38px;padding:6px 8px;margin-right:4px;text-align:center;border-radius:8px;background:#ecebe5;font-weight:700}
.frame.new{background:#fde7c8;outline:2px solid #e3a24a}.frame.empty{color:#aaa;font-weight:400}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}.tabs button.on{background:var(--ink);color:#fff}
.chart{background:#fcfcfb;border:1px solid var(--line);border-radius:14px;padding:12px;overflow:auto}
.ok{color:var(--hit);font-weight:600}.warn{color:var(--miss);font-weight:600}
footer{margin-top:56px;color:var(--muted);font-size:14px}
@media print{.controls,.tabs{display:none}}
"""

_JS = """
const D = JSON.parse(document.getElementById('data').textContent);
const n = D.refs.length; let t = 0, timer = null;
const $ = s => document.querySelector(s);
const strip = $('#strip');
D.refs.forEach((p, i) => { const s = document.createElement('span'); s.textContent = p; s.className='mono';
  s.title = 'Adım ' + (i + 1); s.onclick = () => go(i); strip.appendChild(s); });
function frames(st){ return st.frames.map((p, k) => p === null ? '<span class="frame empty mono">·</span>'
  : '<span class="frame mono' + (k === st.slot ? ' new' : '') + '">' + p + '</span>').join(''); }
function go(i){ t = Math.max(0, Math.min(n - 1, i)); $('#slider').value = t;
  $('#pos').textContent = 'Adım ' + (t + 1) + ' / ' + n + ' — sayfa ' + D.refs[t];
  [...strip.children].forEach((s, k) => s.className = 'mono' + (k < t ? ' past' : k === t ? ' now' : ''));
  $('#vbody').innerHTML = D.algos.map(a => { const st = a.steps[t];
    const f = a.steps.slice(0, t + 1).filter(x => !x.hit).length;
    return '<tr><td><b>' + a.name + '</b></td><td>' + frames(st) + '</td><td class="' + (st.hit ? 'hit">HIT' : 'miss">MISS')
      + '</td><td class="mono">' + (st.evicted ?? '') + '</td><td class="n">' + f + '</td><td class="muted mono">' + st.note + '</td></tr>'; }).join(''); }
function play(){ if (timer) { clearInterval(timer); timer = null; $('#play').textContent = '▶ Oynat'; return; }
  if (t >= n - 1) go(0); $('#play').textContent = '⏸ Durdur';
  timer = setInterval(() => { if (t >= n - 1) { play(); return; } go(t + 1); }, 900); }
$('#slider').max = n - 1; $('#slider').oninput = e => go(+e.target.value);
$('#prev').onclick = () => go(t - 1); $('#next').onclick = () => go(t + 1); $('#play').onclick = play;
document.addEventListener('keydown', e => { if (e.key === 'ArrowRight') go(t + 1); if (e.key === 'ArrowLeft') go(t - 1);
  if (e.key === ' ') { e.preventDefault(); play(); } });
document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => {
  document.querySelectorAll('.tabs button').forEach(x => x.classList.toggle('on', x === b));
  document.querySelectorAll('.algo').forEach(x => x.hidden = x.dataset.algo !== b.dataset.algo); });
go(0);
"""


def _pct(x: float) -> str:
    return f"%{100 * x:.1f}".replace(".", ",")


def _step_table(r: SimulationResult) -> str:
    head = "".join(f"<th>Ç{i}</th>" for i in range(r.frame_count))
    rows = []
    for s in r.steps:
        cells = "".join(
            f'<td class="mono">{"·" if p is None else p}{"*" if k == s.loaded_into else ""}</td>'
            for k, p in enumerate(s.frames))
        res = '<td class="hit">HIT</td>' if s.hit else '<td class="miss">MISS</td>'
        ev = "" if s.evicted is None else s.evicted
        rows.append(f'<tr><td class="n">{s.index}</td><td class="n mono">{s.page}</td>{cells}{res}'
                    f'<td class="mono">{ev}</td><td class="muted mono">{escape(s.note)}</td></tr>')
    return (f'<table><tr><th class="n">Adım</th><th class="n">Sayfa</th>{head}<th>Sonuç</th>'
            f'<th>Çıkan</th><th>Algoritma durumu</th></tr>{"".join(rows)}</table>')


def build(results: List[SimulationResult], table: Dict[str, List[int]], lo: int,
          anomalies: List[Anomaly], source: str = "") -> str:
    refs = list(results[0].references)
    k = results[0].frame_count
    best = min(r.faults for r in results)
    opt = next((r for r in results if r.short_name == "OPT"), None)
    data = {
        "refs": refs,
        "algos": [{"name": r.short_name,
                   "steps": [{"frames": list(s.frames), "hit": s.hit, "evicted": s.evicted,
                              "slot": s.loaded_into, "note": s.note} for s in r.steps]}
                  for r in results],
    }
    cards = [("Toplam erişim", len(refs)), ("Farklı sayfa", len(set(refs))), ("Çerçeve", k),
             ("En az hata", f"{best} ({', '.join(r.short_name for r in results if r.faults == best)})")]
    if opt:
        worst = max(results, key=lambda r: r.faults)
        cards.append((f"{worst.short_name} − OPT", f"+{worst.faults - opt.faults}"))
    cards_html = "".join(f'<div class="card"><div class="lbl">{escape(str(a))}</div>'
                         f'<div class="big">{escape(str(b))}</div></div>' for a, b in cards)

    comp_rows = []
    for r in sorted(results, key=lambda r: (r.faults, r.short_name)):
        color = SERIES.get(r.short_name, ("#6250d6",))[0]
        gap = "" if opt is None else (f"+{r.faults - opt.faults}" if r.faults > opt.faults else "0")
        bar = f'<div style="height:10px;border-radius:5px;background:{color};width:{100 * r.faults / max(1, max(x.faults for x in results)):.0f}%"></div>'
        comp_rows.append(
            f'<tr class="{"best" if r.faults == best else ""}"><td><b>{r.short_name}</b> '
            f'<span class="muted">{escape(r.algorithm)}</span></td><td class="n">{r.total}</td>'
            f'<td class="n"><b>{r.faults}</b></td><td class="n">{r.hits}</td><td class="n">{_pct(r.hit_ratio)}</td>'
            f'<td class="n">{gap}</td><td style="width:22%">{bar}</td></tr>')

    hi = lo + len(next(iter(table.values()))) - 1
    chart = svg_line_chart(table, lo, "Çerçeve sayısına göre sayfa hatası",
                           f"Aynı referans dizisi, {lo}–{hi} çerçeve", anomalies)
    chart = chart.replace('width="760" height="440"', 'width="100%" style="max-width:960px;height:auto"', 1)
    if anomalies:
        bel = "<br>".join(f'<span class="warn">⚠ Belady anomalisi — {a.algorithm}: {a.frames_before} çerçeve → '
                          f'{a.faults_before} hata, {a.frames_after} çerçeve → {a.faults_after} hata</span>'
                          for a in anomalies)
    else:
        bel = '<span class="ok">✓ Bu aralıkta Belady anomalisi yok.</span>'
    if "OPT" in table:
        bel += ('<br><span class="ok">✓ Optimal her çerçeve sayısında alt sınır.</span>'
                if optimal_is_lower_bound(table) else '<br><span class="warn">✗ Optimal alt sınır değil!</span>')
    range_head = "".join(f'<th class="n">{c}</th>' for c in range(lo, hi + 1))
    range_rows = "".join(
        f'<tr><td><b>{a}</b></td>' + "".join(
            f'<td class="n{" warn" if i and v > f[i - 1] else ""}">{v}{" ▲" if i and v > f[i - 1] else ""}</td>'
            for i, v in enumerate(f)) + "</tr>" for a, f in table.items())

    tabs = "".join(f'<button data-algo="{r.short_name}" class="{"on" if i == 0 else ""}">{r.short_name} ({r.faults})</button>'
                   for i, r in enumerate(results))
    algo_divs = "".join(
        f'<div class="algo" data-algo="{r.short_name}"{"" if i == 0 else " hidden"}>'
        f'<h3>{escape(r.algorithm)} — {r.faults} sayfa hatası, {r.hits} isabet ({_pct(r.hit_ratio)})</h3>'
        f'{_step_table(r)}</div>' for i, r in enumerate(results))

    stamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sayfa Değiştirme Simülasyon Raporu</title><style>{_CSS}</style></head><body><main>
<p class="muted mono">BİM 361 İşletim Sistemleri · Sayfa Değiştirme Algoritmaları Simülatörü v{__version__}</p>
<h1>Simülasyon Raporu</h1>
<p class="muted">Kaynak: {escape(source or "girdi")} · {k} çerçeve · {stamp}</p>
<p class="refs mono">{" ".join(map(str, refs))}</p>
<div class="cards">{cards_html}</div>

<h2>Karşılaştırma</h2>
<table><tr><th>Algoritma</th><th class="n">Erişim</th><th class="n">Sayfa hatası</th><th class="n">İsabet</th>
<th class="n">İsabet oranı</th><th class="n">OPT'a fark</th><th>Hata</th></tr>{"".join(comp_rows)}</table>

<h2>Adım adım oynatıcı</h2>
<div class="viewer">
<div class="controls"><button id="prev">◀</button><button id="play" class="primary">▶ Oynat</button><button id="next">▶</button>
<input id="slider" type="range" min="0" value="0"><span id="pos" class="mono"></span></div>
<div id="strip" class="strip"></div>
<table><tr><th>Alg.</th><th>Çerçeveler</th><th>Sonuç</th><th>Çıkan</th><th class="n">Σ hata</th><th>Neden / durum</th></tr>
<tbody id="vbody"></tbody></table>
<p class="muted">Klavye: ← → adım, boşluk oynat/durdur. Turuncu çerçeve bu adımda yüklenen sayfadır.</p>
</div>

<h2>Çerçeve sayısı analizi</h2>
<div class="chart">{chart}</div>
<p>{bel}</p>
<table><tr><th>Algoritma</th>{range_head}</tr>{range_rows}</table>

<h2>Algoritma bazında adım tabloları</h2>
<div class="tabs">{tabs}</div>{algo_divs}

<footer>Python standart kütüphanesiyle üretildi · tek dosya, internet gerektirmez · Sabina Gasimova</footer>
</main><script type="application/json" id="data">{payload}</script><script>{_JS}</script></body></html>"""


def write(html: str, out_dir: str, name: str = "rapor.html") -> Path:
    path = Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    path = path / name
    path.write_text(html, encoding="utf-8")
    return path
