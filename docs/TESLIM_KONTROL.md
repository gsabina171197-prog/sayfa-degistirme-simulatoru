# 11 Kasım 2026 · 09.00 — Bireysel ara teslim kontrolü

**Hocanın dört zorunlu kriteri:** (1) Depo + README, (2) Veri modeli + iskelet, (3) Çalışan mini demo, (4) Bireysel görev dağılımı.

## Bilgisayarda gösterim sırası (4–6 dakika)

```bash
python --version
python -m unittest discover -s tests
python main.py -f data/ornek.txt -k 3 --step
```

`--step` modunda 8. adıma kadar Enter'a bas; algoritmaların çıkarma kararlarını karşılaştır; ardından `a` + Enter ile bitir. İnternet gerekmez.

Zaman varsa:

```bash
python main.py -f data/belady.txt --range 1 6
python main.py -f data/ornek.txt -k 3
```

`results/rapor.html` dosyasını tarayıcıda açabilirsin. Hatalı girdi örneği `data/hatali_ornek.txt` dosyasıdır; program reddeder.

## Son kontrol

- [ ] ZIP açıldı ve proje klasöründeki `main.py` bulundu
- [ ] Python 3.10 veya üstü kurulu
- [ ] 59 otomatik test başarılı
- [ ] `--step` modu çalışıyor
- [ ] `Proje_Oneri_Formu_Bireysel.docx` / PDF açılabiliyor
- [ ] `BIM361_Bireysel_Ara_Teslim.pptx` açılabiliyor
- [ ] `docs/BIREYSEL_GOREV_DAGILIMI.md` hazır
- [ ] GitHub bağlantısı oluşturuldu **ve push doğrulandı** (bu aşama bu paketle otomatik tamamlanmaz)
- [ ] Sunumda ölçülmemiş gerçek işletim sistemi performansı iddia edilmiyor

## Teslim için kısa açıklama

“Hocam, grup yapısının sona ermesi üzerine proje teslimini bireysel gerçekleştiriyorum. Kod deposu, README, temel veri modelleri, algoritma iskeletleri ve çalışan mini demo hazır. Tüm modüllerin sorumluluğu ve bir sonraki aşama dosyada belirtilmiştir. Aynı 20 referans dizisinde 6 algoritmanın sonucunu ve 59 testin yerel doğrulamasını gösterebilirim.”
