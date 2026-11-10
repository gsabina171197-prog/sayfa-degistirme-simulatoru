# BİM 361 — Bireysel görev paylaşımı ve durum

**Proje:** Sayfa Değiştirme Algoritmaları Simülatörü  
**Teslim:** 11 Kasım 2026 09.00  
**Tek sorumlu öğrenci:** Sabina Gasimova · 202303011138

Grup çalışması sonlandığı için bu teslim bireysel yürütülmektedir. Ekip üyesi görevi veya katkısı varmış gibi gösterilmemiştir.

| İş paketi | Sorumlu | Mevcut dosyalar | Kanıt / durum |
|---|---|---|---|
| Temel veri modeli ve yürütücü | Sabina Gasimova | `core.py`, `main.py` | `Step`, `SimulationResult`, `run`, CLI; çalışıyor |
| Girdi, doğrulama ve ekran çıktısı | Sabina Gasimova | `input_io.py`, `display.py` | Geçerli/hatalı girdi örnekleri; çalışıyor |
| FIFO, LRU, Optimal | Sabina Gasimova | `fifo.py`, `lru.py`, `optimal.py` | Ortak arayüz altında çalışıyor |
| Clock, LFU, Aging | Sabina Gasimova | `clock.py`, `lfu.py`, `aging.py` | Ortak arayüz altında çalışıyor |
| Analiz, dışa aktarma, örnek izler | Sabina Gasimova | `analysis.py`, `export.py`, `html_report.py`, `trace.py` | PoC kapsamını aşan ek özellikler; çalışıyor |
| Test ve dokümantasyon | Sabina Gasimova | `tests/`, `README.md`, `docs/` | Yerel `unittest` koşusunda 59/59 başarılı |

**Sonraki ara değerlendirmeye kadar:** hocanın geri bildirimlerine göre kapsamı sadeleştirmek, deneylerin varsayımlarını açıklamak, test senaryolarını genişletmek ve GitHub bağlantısını paylaşmak. Herhangi bir eşlikçi öğrenciye görev atanmamıştır.

**Sunumda kullanılabilecek açıklama:** “Grup yapısı sona erdiği için proje sorumluluğunu bireysel üstlendim. Ortak yürütücü, algoritmalar, girdi doğrulama, demo ve testler mevcut. Bugün öncelikle hocamızın dört ara teslim kriterini çalışan kodla göstereceğim.”
