# Sayfa Değiştirme Algoritmaları Simülatörü

BİM 361 İşletim Sistemleri dersi dönem projesi — Doğuş Üniversitesi, Yazılım Mühendisliği.

**Hazırlayan:** Sabina Gasimova (202303011138) · **Sürüm:** 1.0 (final)

![testler](../../actions/workflows/tests.yml/badge.svg)

Sanal bellekte fiziksel çerçeveler dolduğunda hangi sayfanın çıkarılacağına karar veren
**FIFO, LRU, Optimal, Second Chance (Clock), LFU ve Aging** algoritmalarını **aynı referans dizisi
ve aynı çerçeve sayısı** üzerinde adım adım çalıştıran, karşılaştıran ve gerçek program izleriyle
deneyen komut satırı simülatörü.

## Özellikler

| Özellik | Açıklama |
|---|---|
| 6 algoritma | FIFO, LRU, Optimal, Clock, LFU, Aging — tek ortak arayüz |
| Adım adım tablo | Her erişimde çerçeveler, HIT/MISS, çıkan sayfa ve algoritmanın karar gerekçesi |
| Canlı demo | `--step`: her Enter'da bir erişim, altı algoritma yan yana |
| Karşılaştırma | Hata, isabet, oranlar, Optimal'e fark |
| Çerçeve aralığı analizi | Her çerçeve sayısı için hata, **Belady anomalisinin otomatik tespiti** |
| Sentetik iş yükleri | Düzgün rastgele, yerellik, döngüsel tarama, karma (tekrarlanabilir) |
| Gerçek program izleri | Matris (satır/sütun), matris çarpımı, quicksort, ikili arama; Valgrind Lackey izi okuma |
| Çıktılar | Çalışma logu, CSV, JSON, SVG grafik (log ölçek), etkileşimli tek dosyalık HTML rapor |
| Menü | Argümansız `python main.py` ile tüm senaryolar tek tuşla |
| Test ve CI | 59 test; GitHub Actions ile Ubuntu + Windows, Python 3.10 / 3.12 |

## Gereksinimler

Python 3.10 veya üstü. **Yalnızca standart kütüphane** kullanılır; ek paket kurulumu gerekmez.
Windows'ta `python` yerine `py`, bazı Linux sistemlerinde `python3` kullanın.

## Hızlı başlangıç

```bash
python main.py                                          # menü
python main.py --file data/ornek.txt --frames 3 --open  # test senaryosu + HTML rapor
python main.py --file data/ornek.txt --frames 3 --step  # canlı adım adım demo
python main.py --file data/belady.txt --range 1 6       # Belady anomalisi
python main.py --workloads --range 2 8                  # sentetik iş yükleri
python main.py --experiment                             # gerçek program izleri deneyi
python main.py --trace data/izler/matris_carpim_8.lackey --page-size 256 --range 1 8
python -m unittest discover -s tests                    # testler
```

## Komut satırı seçenekleri

| Seçenek | Açıklama |
|---|---|
| `--file, -f DOSYA` | Referans dizisini dosyadan oku |
| `--refs, -r "7 0 1"` | Referans dizisini doğrudan ver |
| `--random N` | N uzunlukta tekrarlanabilir rastgele dizi (`--pages`, `--seed`) |
| `--trace, -t DOSYA` | Bellek erişim izi: Valgrind Lackey biçimi veya satır başına bir adres (`--page-size`, vars. 4096) |
| `--program AD` | İzlenen program: `matris_satir`, `matris_sutun`, `matris_carpim`, `quicksort`, `ikili_arama` (`--page-size`, vars. 512) |
| `--workloads` | Sentetik iş yükü analizi (`--length`) |
| `--experiment` | Tüm izlenen programlarda deney (vars. 1–40 çerçeve) |
| `--frames, -k K` | Çerçeve sayısı |
| `--range MIN MAX` | Çerçeve aralığı analizi, Belady tespiti, SVG grafik |
| `--algo, -a ...` | Sadece seçilen algoritmalar: `fifo lru optimal clock lfu aging` |
| `--step` | Canlı demo (Enter: ilerle, `a`: sona kadar oynat, `q`: çık) |
| `--summary, -s` | Adım tablolarını gizle |
| `--open` | `rapor.html` dosyasını tarayıcıda aç |
| `--out, -o KLASÖR` | Çıktı klasörü (vars. `results/`) |
| `--no-export`, `--no-color`, `--no-notes`, `--no-collapse`, `--save-refs DOSYA` | Diğer |

Girdi dosyası: sayılar boşluk, virgül, noktalı virgül veya satır sonuyla ayrılır; `#` sonrası yorumdur.
Boş girdi, negatif / tam sayı olmayan değer ve geçersiz çerçeve sayısı konum bilgisiyle reddedilir (çıkış kodu 2).
500 erişimden uzun dizilerde adım tabloları atlanır ve hızlı mod kullanılır.

## Sonuçlar

**Test senaryosu** — `3 5 3 0 5 6 5 1 5 1 3 1 4 2 1 0 5 2 0 5`, 3 çerçeve:

| Algoritma | Sayfa hatası | İsabet | İsabet oranı | Optimal'e fark |
|---|---:|---:|---:|---:|
| Optimal | 8 | 12 | %60,0 | 0 |
| LFU | 10 | 10 | %50,0 | +2 |
| LRU | 11 | 9 | %45,0 | +3 |
| Clock | 12 | 8 | %40,0 | +4 |
| Aging | 12 | 8 | %40,0 | +4 |
| FIFO | 13 | 7 | %35,0 | +5 |

Adım adım çözüm: [`docs/adim_adim_cozum.md`](docs/adim_adim_cozum.md)

**Belady anomalisi** — `5 2 3 4 5 2 1 5 2 3 2 4 1`: FIFO 3 çerçevede 9, 4 çerçevede 10 hata.

**Gerçek program izleri** (sayfa 512 B, 1–40 çerçeve):

- Aynı matrisi sütun sütun toplamak, 8 çerçevede satır satır toplamaya göre **48 kat** fazla sayfa hatası üretir.
- Belady anomalisi gerçek izlerde de görülür: Clock (quicksort, matris çarpımı), LFU (quicksort, ikili arama), Aging (matris çarpımı). LRU ve Optimal hiçbirinde göstermez.
- LFU quicksort izinde 8 çerçevede 12.658 hata yapar; LRU 281, Aging 275.

Ayrıntılı yorum final raporundadır.

## Mimari

```
main.py                    CLI: argümanlar, menü, mod seçimi, konsol + log
simulator/
  core.py                  Step, SimulationResult, PageReplacementAlgorithm (ortak arayüz), kayıt, hızlı mod
  fifo.py  lru.py  optimal.py  clock.py  lfu.py  aging.py
  input_io.py              Dosya/metin ayrıştırma, doğrulama, iş yükü üreteçleri
  trace.py                 Adres izi okuma (Lackey / düz), izlenen programlar
  analysis.py              Çerçeve aralığı, Belady tespiti, OPT alt sınır kontrolü, iş yükü analizi
  display.py               Adım tablosu, ızgara, karşılaştırma, renkli konsol
  export.py                CSV, JSON, SVG grafik, log
  html_report.py           Etkileşimli HTML rapor
tests/                     59 test (unittest)
data/                      ornek.txt, belady.txt, hatali_ornek.txt, izler/matris_carpim_8.lackey
docs/                      adım adım çözüm, sunum rehberi, öneri formu, GitHub yükleme
```

Çerçeve tablosu ve HIT/MISS kararı `PageReplacementAlgorithm.run()` içinde tek yerde yapılır
(Template Method). Algoritmalar yalnızca `choose_victim` ve veri yapısı kancalarını
(`on_hit`, `on_load`, `on_evict`, `on_reference`) uygular. Yeni algoritma = tek dosya + `@register`.

| Algoritma | Veri yapısı | Maliyet |
|---|---|---|
| FIFO | `deque` | O(1) |
| LRU | `OrderedDict` | O(1) |
| Optimal | Sonraki kullanım tablosu (tek geri geçiş, O(n)) | Hata başına O(k) |
| Clock | Referans biti + dairesel el | Amortize O(1) |
| LFU | Sayaç + yükleme zamanı | Hata başına O(k) |
| Aging | 8 bitlik sayaç + R biti, periyodik tik | Tik başına O(k) |

## Geliştirme süreci

Her bileşen ayrı bir `feature/*` dalında geliştirilip `--no-ff` merge ile `main`'e alınmıştır:
ortak arayüz → FIFO → LRU → Optimal → girdi/CLI → Clock/LFU → HTML rapor → testler/CI →
Aging → iz deneyi → final dokümantasyon. Etiketler: `v0.8-ara-teslim`, `v1.0-final`.
