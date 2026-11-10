# BİM 361 — Bireysel ara teslim sunum metni (4–6 dakika)

## Açılış (0:00–0:40)

“Hocam, iyi günler. Ben Yazılım Mühendisliği öğrencisi Sabina Gasimova, numaram 202303011138. Grup yapısı sona erdiğinden bu ara teslimi tek başıma gerçekleştiriyorum. Projem sayfa değiştirme algoritmalarını ortak bir senaryo üzerinden karşılaştıran bir simülatör. Bugün önceliğim sizden istenen dört temel kanıtı göstermek: kod deposu ve README, veri modeli ve iskelet, çalışan mini demo, bireysel sorumluluk dağılımı.”

## Problem (0:40–1:10)

“Fiziksel çerçeveler doluyken yeni bir sanal bellek sayfası istendiğinde mevcut sayfalardan biri çıkarılır. Seçim politikasına bağlı olarak sayfa hatası sayısı değişir. FIFO, LRU, Optimal, Clock, LFU ve Aging algoritmalarını aynı referans dizisinde, aynı çerçeve kapasitesiyle test ederek farkları görülebilir hale getirdim. Optimal gelecekteki erişimleri bildiği için gerçek sistemde uygulanmaz; teorik karşılaştırma noktasıdır.”

## Depo + kod iskeleti (1:10–2:00)

“README dosyasında Python 3.10+ kurulumu, tek komutla çalıştırma, dizin mimarisi ve testler var. `core.py` dosyasında her erişim sonrası durumu saklayan `Step`, toplam sonuçları tutan `SimulationResult` ve ortak `PageReplacementAlgorithm` sınıfını gösterebilirim. `run()` sayfa isabetini ve hatasını tek yerde yönetiyor; her algoritma `choose_victim()` üzerinden çıkaracağı sayfayı seçiyor.”

## Canlı mini demo (2:00–3:20)

“Şimdi aynı 20 erişimlik diziyi üç bellek çerçevesiyle çalıştıracağım.”

```bash
python main.py -f data/ornek.txt -k 3 --step
```

“İlk yedi adımı ilerletiyorum. Sekizinci adımda sayfa 1 isteniyor. FIFO 5'i, LRU ve Clock 0'ı, LFU ve Optimal 6'yı, Aging ise 3'ü çıkarıyor. Dolayısıyla aynı girdide algoritmaların farklı kararları anlık olarak görülebiliyor. Tam çalışmanın sonunda FIFO 13, LRU 11, Optimal 8, Clock 12, LFU 10, Aging 12 sayfa hatası üretiyor.”

## Görevler ve doğrulama (3:20–4:15)

“Grup sona erdiği için modüller ve teslim sorumluluğu tek kişide toplandı; öneri formunun 6. bölümünde her iş paketi bununla birlikte listelendi. Python’un `unittest` sistemiyle 59 yerel test başarılı. Bunlar algoritmaların örnek sonuçlarını, bazı sınır durumlarını, giriş doğrulamayı ve CLI akışlarını kontrol ediyor.”

```bash
python -m unittest discover -s tests
```

## Kapanış (4:15–4:45)

“Öncelikli ara teslim kanıtları bunlar. İsteğe bağlı olarak Belady anomalisini gösterebilir veya üretilen çevrimdışı HTML raporu açabilirim. Proje Python üzerinde bir eğitim simülasyonudur, gerçek işletim sisteminin bellek yöneticisini değiştirmez. Geri bildirimleriniz doğrultusunda kapsamı yeniden önceliklendireceğim. Teşekkür ederim.”

## Hızlı soru–cevap

**Neden Python?** Harici bağımlılık olmadan çekirdek algoritmaları ve eğitimsel arayüzü hızla karşılaştırmak için. Ödevdeki struct/class/header **örnektir**; Python `dataclass` ve soyut sınıfla eşdeğer veri modelini gösteriyor.

**Gerçek RAM'i mi test ediyorsun?** Hayır. Sayfa numaraları ve çerçeveler bir modelde tutuluyor. Ek iş yükü izleri Python `TracedArray` erişimlerinden üretiliyor; gerçek sistemin disk gecikmesi ölçülmüyor.

**Optimal niçin var?** Geleceği bilen algoritma pratik bir politika değildir; algoritmaların karşılaştırılması için teorik alt sınır sağlar.

**Belady anomalisi nedir?** Bazı sayfa değiştirme politikalarında çerçeve sayısı artmasına rağmen hata sayısı artabilir. Verilen dizide FIFO 3 çerçevede 9, 4 çerçevede 10 hata veriyor.

**Neden LRU'da Belady yok?** LRU bir yığın algoritmasıdır; daha büyük çerçeve kapasitesindeki mevcut sayfalar, daha küçük kapasite kümesini kapsar.

**GitHub nerede?** Yerel Git geçmişi, dalları ve README pakette hazır; GitHub hesabına push ayrıca yapılmalı. Yapılmadıysa bağlantının yayımlandığını söyleme.

**AI kullandın mı?** Açıkça belirt: “Dokümantasyon ve kod gözden geçirmede AI desteğinden yararlandım. Çalışmayı yerel testlerle kontrol ettim; demo akışını ve algoritmaların karar mekanizmasını anlatabiliyorum.”

**Sonraki aşama?** Öğretim elemanı geribildirimleri doğrultusunda kapsamı netleştirmek, belge/test iyileştirmeleri ve depoyu GitHub hesabında yayımlamak.

## Yarın sunumdan hemen önce

- Terminali `main.py` olan klasörde aç.
- `python -m unittest discover -s tests` çalıştır; sonucu göster.
- `python main.py -f data/ornek.txt -k 3 --step` çalıştır; 8. adıma kadar Enter, sonra `a`.
- Sunumdaki **3. slayt** hocanın dört asgari kriterini birebir özetliyor.
- GitHub yüklemesi hazır değilse bunu açıkça belirt; olmayan linki göstermeye çalışma.
