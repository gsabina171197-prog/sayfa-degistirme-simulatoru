# Ara Sunum Rehberi — 11 Kasım 2026

Sunan: **Sabina Gasimova** (tek kişilik proje)

## 1. Kontrol listesi karşılığı

| Hocanın kriteri | Bizde karşılığı | Gösterim |
|---|---|---|
| 1. Çalışan çekirdek mantık (canlı demo) | 5 algoritma tek senaryoda baştan sona çalışır | `python main.py -f data/ornek.txt -k 3 --step` |
| 2. Modül entegrasyonu | 11 modül, ortak arayüzle tek `main.py` altında | Tek komut: 5 algoritma + karşılaştırma + rapor |
| 3. Ara çıktılar / metrikler | Konsolda tablolar; dosyada log, CSV, JSON, SVG ve etkileşimli HTML rapor | `results/` klasörü, `results/rapor.html` |
| 4. Git katkı durumu | Her bileşen kendi `feature/*` dalında; `--no-ff` merge'lerle `main` | GitHub → Commits, Network grafiği, Actions sekmesi |
| Geri bildirim: sayıları değiştirin | Yeni dizi `3 5 3 0 5 6 5 1 5 1 3 1 4 2 1 0 5 2 0 5`, yeni Belady dizisi `5 2 3 4 5 2 1 5 2 3 2 4 1` | `data/ornek.txt`, `data/belady.txt` |
| "En fazla %80" | Sürüm 0.8; final raporu, NRU/Aging ve gerçek iz deneyi finale kaldı | README → Yol haritası |

## 2. Sunumdan önce (sabah, 10 dakika)

1. Depoyu klonlayın ya da zip'i açın; klasörde terminal açın.
2. `python --version` → 3.10 veya üstü olmalı (Windows'ta `py --version`).
3. `results` klasörünü silin (demo sırasında yeniden üretilecek).
4. `python -m unittest discover -s tests` → `OK` görün.
5. Terminal yazı boyutunu büyütün (Ctrl + `+`). Windows'ta Windows Terminal kullanın (renkler).
6. Yedek: internet veya projektör sorunu olursa `results/rapor.html` tek başına açılır.

## 3. Demo akışı (≈ 8 dakika)

| Süre | Ne anlatılır | Komut |
|---|---|---|
| 0:00 | Problem, kapsam, ortak arayüz mimarisi (slayt 2–4) | — |
| 1:00 | 43 test geçiyor; CI her push'ta Ubuntu + Windows'ta çalışıyor | `python -m unittest discover -s tests` |
| 1:30 | **Canlı demo:** 6–8 adım Enter ile; 8. adımda beş farklı kararı anlatın, sonra `a` | `python main.py -f data/ornek.txt -k 3 --step` |
| 3:30 | Tam çıktı: adım tabloları, karşılaştırma, rapor tarayıcıda açılır | `python main.py -f data/ornek.txt -k 3 --open` |
| 4:30 | HTML raporda oynatıcı (boşluk tuşu), grafik ve sekmeler | tarayıcı |
| 5:15 | Belady anomalisi ve OPT alt sınır kontrolü | `python main.py -f data/belady.txt --range 1 6` |
| 6:15 | İş yükü analizi — en iyi algoritma iş yüküne göre değişir | `python main.py --workloads --range 2 8 -s` |
| 7:00 | Giriş kontrolü | `python main.py -f data/hatali_ornek.txt -k 3` |
| 7:20 | Git geçmişi (dallar + merge'ler) ve kalan %20 | GitHub |

Hepsi menüden de çalışır: `python main.py` (argümansız) → 1–5.

## 4. Anlatılacak noktalar ve olası sorular

**Mimari (core.py).** `run()` çerçeve tablosunu ve HIT/MISS kararını tek yerde yönetir; algoritmalar
sadece `choose_victim` ve veri yapısı kancalarını yazar (Template Method). Yeni algoritma = yeni dosya
+ `@register`. Karşılaştırma, analiz, rapor algoritmadan bağımsızdır çünkü hepsi `SimulationResult` kullanır.

**FIFO.** `deque`; en önce yükleneni çıkarır. Kullanım bilgisine bakmaz: 8. adımda bir önceki adımda
kullanılan 5'i çıkarır.

**Clock.** Her sayfanın referans biti var. El dolaşır; bit 1 ise 0 yapıp geçer (ikinci şans), bit 0 olan
ilk sayfayı çıkarır. 8. adımda 5 ikinci şans alır, 0 çıkar. FIFO'dan 1 hata daha az (12'ye 13).
- *"Bütün bitler 1 ise?"* → El bir turda hepsini 0 yapar, ikinci turda ilk sayfayı çıkarır; FIFO gibi davranır. En fazla iki tur.

**LRU.** `OrderedDict` son kullanım sırasında; isabette `move_to_end`, kurban ilk anahtar — hepsi O(1).
- *"Neden Belady anomalisi göstermez?"* → Yığın algoritmasıdır: k çerçevedeki sayfa kümesi her zaman k+1 çerçevedekinin alt kümesidir. Testlerde 100 rastgele dizide doğrulanıyor.
- *"Gerçek işletim sistemleri neden saf LRU kullanmaz?"* → Her erişimde sıralamayı güncellemek donanım desteği ister; Clock bunun ucuz yaklaşımıdır (Linux da Clock türevi kullanır).

**LFU.** En az erişilen çıkar; eşitlikte en önce yüklenen. Senaryoda 10 hatayla LRU'dan iyi (1 ve 5 sık).
İş yükü analizinde yerellikte kötü: çalışma kümesi kayınca eski "popüler" sayfalar bellekte kalır.

**Optimal.** Sonraki kullanımı en uzak (∞) sayfayı çıkarır; geleceği bilmek gerektiği için gerçek
sistemde uygulanamaz, alt sınırdır. Sonraki kullanım tablosu diziyi sondan başa **bir kez** tarayarak
O(n)'de hesaplanır; naif yöntem her hatada kalan diziyi tarar.
- *"Eşitlik olursa?"* → Hiç kullanılmayacak birden çok sayfa varsa en önce yükleneni çıkarıyorum; hata sayısını değiştirmez, sonucu deterministik yapar.

**Doğrulama.** FIFO/LRU/OPT 200 rastgele senaryoda, farklı yazılmış basit (naif) uygulamalarla aynı
sonucu veriyor. Ders kitabı örneği (Silberschatz) 15/12/9 ile birebir.

**Yapay zekâ sorusu gelirse:** Dürüst olun. Hangi aracı nasıl kullandığınızı söyleyin ve her modülü
yukarıdaki maddelerle kendiniz anlatabildiğinizi gösterin; değerlendirmede önemli olan kodu anlamanız.

## 5. Git

Zip içindeki depo, dallar ve merge'lerle hazır bir geçmişe sahiptir (`git log --graph --oneline --all`).
GitHub'a gönderme adımları için `docs/GITHUB_YUKLEME.md` dosyasına bakın.
