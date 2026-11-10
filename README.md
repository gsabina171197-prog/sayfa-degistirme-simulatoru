# Sayfa Değiştirme Algoritmaları Simülatörü

BİM 361 İşletim Sistemleri dersi dönem projesi — Doğuş Üniversitesi, Yazılım Mühendisliği.

**Hazırlayan:** Sabina Gasimova (202303011138) — tek kişilik proje

![testler](../../actions/workflows/tests.yml/badge.svg)

Sanal bellekte fiziksel çerçeveler dolduğunda hangi sayfanın çıkarılacağına karar veren
**FIFO, LRU, Optimal, Second Chance (Clock) ve LFU** algoritmalarını **aynı referans dizisi ve
aynı çerçeve sayısı** üzerinde adım adım çalıştıran, karşılaştıran ve analiz eden komut satırı simülatörü.

> **Sürüm 0.8 — ara teslim (11 Kasım 2026).** Projenin yaklaşık %80'i tamamlandı; kalan iş için bkz. [Yol haritası](#yol-haritası).

## Mevcut durum

| Bileşen | Durum |
|---|---|
| Ortak arayüz, veri modeli, algoritma kaydı | ✅ Tamamlandı |
| Girdi okuma ve doğrulama (dosya, satır içi, rastgele) | ✅ Tamamlandı |
| FIFO, LRU, Optimal | ✅ Tamamlandı ve test edildi |
| Second Chance (Clock), LFU | ✅ Tamamlandı ve test edildi |
| Adım adım bellek tablosu + karar açıklaması | ✅ Tamamlandı |
| Etkileşimli HTML rapor (adım oynatıcı, grafik, tablolar) | ✅ Tamamlandı |
| Argümansız çalıştırmada menü | ✅ Tamamlandı |
| GitHub Actions: Ubuntu + Windows, Python 3.10 / 3.12 | ✅ Tamamlandı |
| Karşılaştırma tablosu | ✅ Tamamlandı |
| Çerçeve aralığı analizi + otomatik Belady anomalisi tespiti | ✅ Tamamlandı |
| Canlı adım adım demo modu (`--step`) | ✅ Tamamlandı |
| CSV / JSON / SVG grafik / çalışma logu dışa aktarımı | ✅ Tamamlandı |
| İş yükü türlerine göre performans analizi | ✅ Tamamlandı |
| Birim testleri | ✅ 43 test geçiyor |
| Final raporu ve sunumu | ⏳ Final teslimi |

## Gereksinimler

Python 3.10 veya üstü. **Yalnızca standart kütüphane** kullanılır (`argparse`, `collections`,
`csv`, `json`, `unittest`); ek paket kurulumu gerekmez. Linux, macOS ve Windows'ta çalışır.

## Hızlı başlangıç

```bash
# 0) Menü: argümansız çalıştırınca tüm senaryolar tek tuşla
python main.py

# 1) Test senaryosu: 5 algoritma, adım tabloları + karşılaştırma
python main.py --file data/ornek.txt --frames 3

# 1b) Aynısı + HTML raporu tarayıcıda aç
python main.py --file data/ornek.txt --frames 3 --open

# 2) Canlı demo: her Enter'da bir erişim, tüm algoritmalar yan yana
python main.py --file data/ornek.txt --frames 3 --step

# 3) Çerçeve aralığı analizi ve Belady anomalisi
python main.py --file data/belady.txt --range 1 6

# 4) Farklı iş yüklerinde performans analizi
python main.py --workloads --range 2 8

# 5) Testler
python -m unittest discover -s tests -v
```

Windows'ta `python` yerine `py`, bazı Linux sistemlerinde `python3` kullanın.

## Komut satırı seçenekleri

| Seçenek | Açıklama |
|---|---|
| `--file, -f DOSYA` | Referans dizisini dosyadan oku |
| `--refs, -r "7 0 1"` | Referans dizisini doğrudan ver |
| `--random N` | N uzunlukta tekrarlanabilir rastgele dizi (`--pages`, `--seed` ile) |
| `--workloads` | Düzgün rastgele, yerellik, döngüsel tarama ve karma iş yüklerinde analiz (`--length`) |
| `--frames, -k K` | Çerçeve sayısı |
| `--range MIN MAX` | MIN..MAX çerçeve için hata sayıları, Belady tespiti, SVG grafik |
| `--algo, -a ...` | Sadece seçilen algoritmalar: `fifo lru optimal clock lfu` |
| `--step` | Canlı demo modu (Enter: ilerle, `a`: sona kadar oynat, `q`: çık) |
| `--summary, -s` | Adım tablolarını gizle, sadece özet |
| `--out, -o KLASÖR` | Çıktı klasörü (varsayılan `results/`) |
| `--no-export` | Dosya yazma |
| `--save-refs DOSYA` | Kullanılan diziyi dosyaya kaydet (rastgele diziyi saklamak için) |
| `--open` | Üretilen `rapor.html` dosyasını tarayıcıda aç |
| `--no-color`, `--no-notes` | Renksiz çıktı / algoritma durum sütununu gizle |

Girdi dosyası biçimi: sayılar boşluk, virgül, noktalı virgül veya satır sonuyla ayrılır;
`#` sonrası yorumdur. Boş girdi, negatif veya tam sayı olmayan değer ve geçersiz çerçeve
sayısı satır/sıra bilgisiyle reddedilir (çıkış kodu 2).

## Test senaryosu ve sonuçlar

Referans dizisi: `3 5 3 0 5 6 5 1 5 1 3 1 4 2 1 0 5 2 0 5` — 20 erişim, 7 farklı sayfa — **3 çerçeve**

| Algoritma | Toplam Erişim | Sayfa Hatası | İsabet | İsabet Oranı | OPT'a fark |
|---|---:|---:|---:|---:|---:|
| Optimal | 20 | 8 | 12 | %60,0 | 0 |
| LFU | 20 | 10 | 10 | %50,0 | +2 |
| LRU | 20 | 11 | 9 | %45,0 | +3 |
| Clock | 20 | 12 | 8 | %40,0 | +4 |
| FIFO | 20 | 13 | 7 | %35,0 | +5 |

Adım adım çözüm: [`docs/adim_adim_cozum.md`](docs/adim_adim_cozum.md).

**Belady anomalisi** (`data/belady.txt`: `5 2 3 4 5 2 1 5 2 3 2 4 1`): FIFO 3 çerçevede **9**,
4 çerçevede **10** sayfa hatası verir. LRU ve Optimal yığın (stack) algoritmaları olduğu için
anomali göstermez; bu özellik 100 rastgele senaryoda test edilir.

## Çıktılar (`results/`)

| Dosya | İçerik |
|---|---|
| `rapor.html` | **Etkileşimli rapor**: özet kartlar, karşılaştırma, adım adım oynatıcı (← → / boşluk), çerçeve–hata grafiği, Belady kontrolü, algoritma bazında adım tabloları. Tek dosya, internet gerektirmez |
| `calisma_logu.txt` | Her çalıştırmanın konsol çıktısı, zaman damgalı (renksiz) |
| `adimlar.csv` | Her algoritmanın her adımı: çerçeveler, HIT/MISS, çıkan sayfa, karar açıklaması |
| `ozet.csv`, `sonuclar.json` | Toplam erişim, hata, isabet, oranlar |
| `cerceve_analizi.csv`, `grafik_cerceve_hata.svg` | Çerçeve sayısı–hata tablosu ve grafiği (Belady bölgesi işaretli) |
| `is_yuku_analizi.csv`, `grafik_<iş yükü>.svg` | İş yükü performans analizi |

CSV dosyaları `;` ayraçlı ve UTF-8 BOM'ludur; Excel'de doğrudan Türkçe karakterlerle açılır.
SVG grafikler tarayıcıda açılır; noktaların üzerine gelince değer görünür.

## Mimari

```
main.py                    CLI: argümanlar, mod seçimi, konsol + log çıktısı
simulator/
  core.py                  Step, SimulationResult, PageReplacementAlgorithm (ortak arayüz), kayıt
  fifo.py   clock.py       FIFO (deque), Second Chance (referans biti + dairesel el)
  lru.py    lfu.py         LRU (OrderedDict), LFU (sayaç + FIFO eşitlik bozma)
  optimal.py               Optimal: tek geri geçişte O(n) sonraki kullanım tablosu
  input_io.py              Dosya/metin ayrıştırma, doğrulama, tekrarlanabilir iş yükü üreteçleri
  analysis.py              Çerçeve aralığı, Belady tespiti, OPT alt sınır kontrolü, iş yükü analizi
  display.py               Adım tablosu, ızgara görünümü, karşılaştırma, renkli konsol
  export.py                CSV, JSON, SVG grafik, çalışma logu
  html_report.py           Tek dosyalık etkileşimli HTML rapor
tests/                     43 birim/entegrasyon testi (unittest)
.github/workflows/         CI: her push'ta testler Ubuntu ve Windows'ta
data/                      ornek.txt, belady.txt, hatali_ornek.txt
docs/                      adım adım çözüm, ara sunum rehberi, öneri formu (revizyon)
```

**Ortak arayüz (Template Method).** Çerçeve tablosu, HIT/MISS kararı ve adım kaydı
`PageReplacementAlgorithm.run()` içinde tek yerde yapılır. Her algoritma sadece
"bellek doluyken hangi sayfa çıkarılmalı?" sorusunu (`choose_victim`) ve kendi veri yapısını
güncelleyen kancaları (`on_hit`, `on_load`, `on_evict`) uygular. Yeni bir algoritma eklemek
için tek dosya ve `@register("ad")` yeterlidir; karşılaştırma, analiz, görüntüleme ve dışa
aktarma kodu değişmez.

**Karmaşıklık** (n = erişim sayısı, k = çerçeve sayısı):

| Algoritma | Erişim başına | Not |
|---|---|---|
| FIFO | O(1) | deque |
| LRU | O(1) | OrderedDict.move_to_end |
| Clock | amortize O(1), en kötü O(k) | el en fazla iki tur döner |
| LFU | O(k) hata başına | sayaç sözlüğünde minimum |
| Optimal | O(k) hata başına | sonraki kullanım tablosu O(n) ön hesap; naif yöntem hata başına O(n) |

## Doğrulama

- Grup senaryosu için 5 algoritmanın beklenen değerleri ve çıkarılan sayfa sırası
- Silberschatz ders kitabı örneğinin yayımlanmış sonuçları (FIFO 15, LRU 12, OPT 9)
- **200 tekrarlanabilir rastgele senaryoda** FIFO/LRU/OPT, ayrı yazılmış basit (naif) uygulamalarla çapraz kontrol
- 200 senaryoda Optimal'in tüm algoritmalar için alt sınır olduğu
- LRU ve Optimal'de Belady anomalisinin hiç oluşmadığı (yığın özelliği)
- Sınır durumları: 1 çerçeve, yeterli çerçeve, tek erişim, aynı sayfa tekrarı
- Girdi hataları, dosya okuma, CSV/SVG/JSON/HTML çıktıları ve CLI çıkış kodları
- Her push'ta GitHub Actions ile Ubuntu + Windows, Python 3.10 ve 3.12 üzerinde otomatik test

## Geliştirme süreci

Proje tek kişi tarafından geliştirilmiştir. Her bileşen ayrı bir `feature/*` dalında geliştirilip
`--no-ff` merge ile `main`'e alınmıştır; commit geçmişi modül sırasını izler:
ortak arayüz → FIFO → LRU → Optimal → girdi/görselleştirme → analiz → dışa aktarma →
Clock → LFU → HTML rapor → testler/CI → dokümantasyon.

## Yol haritası

Final teslimine kadar (kalan ~%20):

- [ ] Final raporu (yöntem, deneyler, iş yükü analizinin yorumu)
- [ ] Final sunumu
- [ ] Ek politika: NRU / Aging (Clock'un çok bitli genellemesi)
- [ ] Gerçek bir programdan alınmış bellek erişim izi (trace) dosyasıyla deney
