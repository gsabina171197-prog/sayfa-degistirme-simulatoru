# Sayfa Değiştirme Algoritmaları Simülatörü

BİM 361 İşletim Sistemleri dersi dönem projesi — Doğuş Üniversitesi, Yazılım Mühendisliği.

**Bireysel proje:** Sabina Gasimova (202303011138) · **Teslim:** 11 Kasım 2026, 09.00 · **Durum:** Ara teslim / çalışan PoC

**Doğrulama:** 59 otomatik test yerel ortamda başarılı. GitHub Actions yapılandırması depoda mevcuttur; uzaktaki çalışma sonucu GitHub’a yüklemeden önce doğrulanmış sayılmaz.

Sanal bellekte fiziksel çerçeveler dolduğunda hangi sayfanın çıkarılacağına karar veren
**FIFO, LRU, Optimal, Second Chance (Clock), LFU ve Aging** algoritmalarını **aynı referans dizisi
ve aynı çerçeve sayısı** üzerinde adım adım çalıştıran, karşılaştıran ve gerçek program izleriyle
deneyen komut satırı simülatörü. **İlk ara teslim kapsamında çalışan çekirdek ve mini demo esas alınmıştır; ileri analizler opsiyonel gösterimdir.**

## Hocanın ilk ara teslimde istediği dört kanıt

| Zorunlu kriter | Dosya / komut | Gösterilecek somut kanıt |
|---|---|---|
| **1. Kod deposu ve README** | `README.md`, `.git/` | Bağımsız çalıştırma komutları, dizin yapısı, mevcut dallar. **GitHub adresi ancak hesabınızdan push yapınca oluşur.** |
| **2. Veri yapıları ve kod iskeleti** | `simulator/core.py` ve `simulator/{fifo,lru,optimal,clock,lfu,aging}.py` | `Step`, `SimulationResult`, `PageReplacementAlgorithm`, `choose_victim()` |
| **3. Çalışan mini demo / PoC** | `python main.py -f data/ornek.txt -k 3 --step` | Aynı girdide 6 algoritmanın bellek çerçeveleri, HIT/MISS ve çıkarma kararları |
| **4. Görev paylaşımı** | `docs/BIREYSEL_GOREV_DAGILIMI.md` ve `docs/Proje_Oneri_Formu.docx` bölüm 6 | Grup dağıldığı için çalışma **tek kişi** tarafından teslim edilir; modül bazlı sorumluluklar açıkça yazılıdır |

**Sunumdaki öncelik sırası:** Önce bu dört kanıtı gösterin. Belady, HTML rapor, iz deneyleri ve gelişmiş analizler yalnızca zaman kalırsa ek olarak gösterilebilir.

## Özellikler

| Özellik | Açıklama |
|---|---|
| 6 algoritma | FIFO, LRU, Optimal, Clock, LFU, Aging — tek ortak arayüz |
| Adım adım tablo | Her erişimde çerçeveler, HIT/MISS, çıkan sayfa ve algoritmanın karar gerekçesi |
| Canlı demo | `--step`: her Enter'da bir erişim, altı algoritma yan yana |
| Karşılaştırma | Hata, isabet, oranlar, Optimal'e fark |
| Çerçeve aralığı analizi | Her çerçeve sayısı için hata, **Belady anomalisinin otomatik tespiti** |
| Sentetik iş yükleri | Düzgün rastgele, yerellik, döngüsel tarama, karma (tekrarlanabilir) |
| Enstrümante edilmiş program izleri (ek) | Python listesi üzerinden izlenen matris, quicksort ve ikili arama algoritmaları; ayrıca Valgrind Lackey biçiminde iz dosyası okuyucu |
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
python main.py --experiment                             # enstrümante edilmiş algoritma izleri (ek)
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

**Enstrümante edilmiş örnek algoritma izleri** (sayfa 512 B, 1–40 çerçeve; gerçek işletim sistemi üzerinde ölçülmüş donanımsal izler değildir):

- Aynı matrisi sütun sütun toplamak, 8 çerçevede satır satır toplamaya göre **48 kat** fazla sayfa hatası üretir.
- Belady anomalisi gerçek izlerde de görülür: Clock (quicksort, matris çarpımı), LFU (quicksort, ikili arama), Aging (matris çarpımı). LRU ve Optimal hiçbirinde göstermez.
- LFU quicksort izinde 8 çerçevede 12.658 hata yapar; LRU 281, Aging 275.

Deneyler kontrollü/sentetik adres alanı modelinde yürütülür; gerçek işletim sistemi sayfa hatası, disk gecikmesi veya tüm proses belleği ölçülmez. Sonuçlar **bu modelin** çıktılarıdır.

## Mimari

```
main.py                    CLI: argümanlar, menü, mod seçimi, konsol + log
simulator/
  core.py                  Step, SimulationResult, PageReplacementAlgorithm (ortak arayüz), kayıt, hızlı mod
  fifo.py  lru.py  optimal.py  clock.py  lfu.py  aging.py
  input_io.py              Dosya/metin ayrıştırma, doğrulama, iş yükü üreteçleri
  trace.py                 Adres izi okuma (Lackey / düz), enstrümante edilmiş algoritmalar
  analysis.py              Çerçeve aralığı, Belady tespiti, OPT alt sınır kontrolü, iş yükü analizi
  display.py               Adım tablosu, ızgara, karşılaştırma, renkli konsol
  export.py                CSV, JSON, SVG grafik, log
  html_report.py           Etkileşimli HTML rapor
tests/                     59 test (unittest)
data/                      ornek.txt, belady.txt, hatali_ornek.txt, izler/matris_carpim_8.lackey
docs/                      adım adım çözüm, öneri formu, bireysel görev ve teslim rehberi
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

ZIP içindeki Git kayıtlarında bileşenler için `feature/*` dalları ve `--no-ff` merge geçmişi bulunmaktadır:
ortak arayüz → FIFO → LRU → Optimal → girdi/CLI → Clock/LFU → HTML rapor → testler/CI →
Aging → iz deneyi → final dokümantasyon. Etiketler: `v0.8-ara-teslim`, `v1.0-final`.

## Bilinen kapsam sınırları ve akademik açıklık

- Bu bir **eğitsel sayfa değiştirme simülasyonudur**; gerçek işletim sistemi çekirdeği, fiziksel RAM veya disk cihazına müdahale etmez.
- Program içi izler özel `TracedArray` veri yapısından üretilir. Gerçek uygulamadan alınmış Valgrind kaydı ayrı olarak içe aktarılabilir; örnek Lackey dosyasının kaynağı ayrıca doğrulanmalıdır.
- Varsayılan ardışık aynı sayfa birleştirme seçeneği LFU/Aging gibi erişim geçmişine duyarlı algoritmalarda sonucu değiştirebilir; birebir iz analizi için `--no-collapse` seçilmelidir.
- Belirtilen 59 test bu yerel paket üzerinde yeniden çalıştırılmıştır. CI'nin GitHub'da başarıyla çalıştığını söylemek için GitHub Actions ekranı kontrol edilmelidir.
- AI destekli yazım/kod gözden geçirme araçlarından yararlanılmıştır. Kaynak kodu, algoritmik kararları ve demo sonuçlarını sözlü açıklayabilmek teslim eden öğrencinin sorumluluğundadır.

## GitHub'a yayımlama (son adım)

1. GitHub hesabınızda **boş**, README eklenmemiş `sayfa-degistirme-simulatoru` deposu oluşturun.
2. Proje klasöründe `git status` ve `git log --oneline -5` ile yerel geçmişi görüntüleyin.
3. `git remote add origin https://github.com/KULLANICI_ADI/sayfa-degistirme-simulatoru.git` (zaten origin varsa `git remote set-url origin ...`).
4. `git push -u origin main` ardından `git push origin --all` ve isterseniz `git push origin --tags`.
5. Depo linkini hoca ile paylaşın. İşlem **bu paket hazırlanırken yapılmamıştır**.

Git geçmişini korumak için `--force` kullanmanız gerekmez. Ayrıntı: `docs/GITHUB_YUKLEME_GUVENLI.md`.
