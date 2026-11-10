# Adım Adım Çözüm — Grup Test Senaryosu

Referans dizisi: `3 5 3 0 5 6 5 1 5 1 3 1 4 2 1 0 5 2 0 5` (20 erişim, 7 farklı sayfa), **3 çerçeve**.

Tablolarda `*` o adımda sayfanın yüklendiği çerçeveyi, `F` sayfa hatasını gösterir. Son sütun, algoritmanın kararını verdiği veri yapısının adım sonundaki durumudur. Tablolar simülatörün çıktısıdır; aynı değerler `tests/test_algorithms.py` içinde beklenen sonuç olarak test edilir ve FIFO, LRU, OPT ayrıca bağımsız yazılmış basit uygulamalarla çapraz doğrulanır.

| Algoritma | Sayfa hatası | İsabet | İsabet oranı |
|---|---|---|---|
| FIFO | 13 | 7 | %35,0 |
| LRU | 11 | 9 | %45,0 |
| OPT | 8 | 12 | %60,0 |
| CLOCK | 12 | 8 | %40,0 |
| LFU | 10 | 10 | %50,0 |

## First-In First-Out (FIFO) — 13 sayfa hatası

Kurban her zaman kuyruğun başındaki (en önce yüklenen) sayfadır. Kullanım sıklığı dikkate alınmaz: 5. adımda kullanılan 5, 8. adımda yine çıkarılır.

```
Ref :  3  5  3  0  5  6  5  1  5  1  3  1  4  2  1  0  5  2  0  5
      -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
Ç0  :  3  3  3  3  3  6  6  6  6  6  3  3  3  3  1  1  1  2  2  2
Ç1  :  .  5  5  5  5  5  5  1  1  1  1  1  4  4  4  0  0  0  0  0
Ç2  :  .  .  .  0  0  0  0  0  5  5  5  5  5  2  2  2  5  5  5  5
Hata:  F  F  ·  F  ·  F  ·  F  F  ·  F  ·  F  F  F  F  F  F  ·  ·   (F = sayfa hatası)
```

<details><summary>Ayrıntılı adım tablosu</summary>

```
+------+-------+----+----+----+-------+-------+---------------------------+
| Adım | Sayfa | Ç0 | Ç1 | Ç2 | Sonuç | Çıkan | Algoritma durumu          |
+======+=======+====+====+====+=======+=======+===========================+
|    1 |     3 | 3* | -  | -  | MISS  |       | kuyruk (eski→yeni): 3     |
|    2 |     5 | 3  | 5* | -  | MISS  |       | kuyruk (eski→yeni): 3 5   |
|    3 |     3 | 3  | 5  | -  | HIT   |       | kuyruk (eski→yeni): 3 5   |
|    4 |     0 | 3  | 5  | 0* | MISS  |       | kuyruk (eski→yeni): 3 5 0 |
|    5 |     5 | 3  | 5  | 0  | HIT   |       | kuyruk (eski→yeni): 3 5 0 |
|    6 |     6 | 6* | 5  | 0  | MISS  | 3     | kuyruk (eski→yeni): 5 0 6 |
|    7 |     5 | 6  | 5  | 0  | HIT   |       | kuyruk (eski→yeni): 5 0 6 |
|    8 |     1 | 6  | 1* | 0  | MISS  | 5     | kuyruk (eski→yeni): 0 6 1 |
|    9 |     5 | 6  | 1  | 5* | MISS  | 0     | kuyruk (eski→yeni): 6 1 5 |
|   10 |     1 | 6  | 1  | 5  | HIT   |       | kuyruk (eski→yeni): 6 1 5 |
|   11 |     3 | 3* | 1  | 5  | MISS  | 6     | kuyruk (eski→yeni): 1 5 3 |
|   12 |     1 | 3  | 1  | 5  | HIT   |       | kuyruk (eski→yeni): 1 5 3 |
|   13 |     4 | 3  | 4* | 5  | MISS  | 1     | kuyruk (eski→yeni): 5 3 4 |
|   14 |     2 | 3  | 4  | 2* | MISS  | 5     | kuyruk (eski→yeni): 3 4 2 |
|   15 |     1 | 1* | 4  | 2  | MISS  | 3     | kuyruk (eski→yeni): 4 2 1 |
|   16 |     0 | 1  | 0* | 2  | MISS  | 4     | kuyruk (eski→yeni): 2 1 0 |
|   17 |     5 | 1  | 0  | 5* | MISS  | 2     | kuyruk (eski→yeni): 1 0 5 |
|   18 |     2 | 2* | 0  | 5  | MISS  | 1     | kuyruk (eski→yeni): 0 5 2 |
|   19 |     0 | 2  | 0  | 5  | HIT   |       | kuyruk (eski→yeni): 0 5 2 |
|   20 |     5 | 2  | 0  | 5  | HIT   |       | kuyruk (eski→yeni): 0 5 2 |
+------+-------+----+----+----+-------+-------+---------------------------+
```
</details>

## Least Recently Used (LRU) — 11 sayfa hatası

Kurban, son kullanımı en eskide kalan sayfadır. Sağdaki liste en eskiden en yeniye son kullanım sırasıdır; listenin ilk elemanı çıkar.

```
Ref :  3  5  3  0  5  6  5  1  5  1  3  1  4  2  1  0  5  2  0  5
      -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
Ç0  :  3  3  3  3  3  6  6  6  6  6  3  3  3  2  2  2  5  5  5  5
Ç1  :  .  5  5  5  5  5  5  5  5  5  5  5  4  4  4  0  0  0  0  0
Ç2  :  .  .  .  0  0  0  0  1  1  1  1  1  1  1  1  1  1  2  2  2
Hata:  F  F  ·  F  ·  F  ·  F  ·  ·  F  ·  F  F  ·  F  F  F  ·  ·   (F = sayfa hatası)
```

<details><summary>Ayrıntılı adım tablosu</summary>

```
+------+-------+----+----+----+-------+-------+---------------------------+
| Adım | Sayfa | Ç0 | Ç1 | Ç2 | Sonuç | Çıkan | Algoritma durumu          |
+======+=======+====+====+====+=======+=======+===========================+
|    1 |     3 | 3* | -  | -  | MISS  |       | eski→yeni kullanım: 3     |
|    2 |     5 | 3  | 5* | -  | MISS  |       | eski→yeni kullanım: 3 5   |
|    3 |     3 | 3  | 5  | -  | HIT   |       | eski→yeni kullanım: 5 3   |
|    4 |     0 | 3  | 5  | 0* | MISS  |       | eski→yeni kullanım: 5 3 0 |
|    5 |     5 | 3  | 5  | 0  | HIT   |       | eski→yeni kullanım: 3 0 5 |
|    6 |     6 | 6* | 5  | 0  | MISS  | 3     | eski→yeni kullanım: 0 5 6 |
|    7 |     5 | 6  | 5  | 0  | HIT   |       | eski→yeni kullanım: 0 6 5 |
|    8 |     1 | 6  | 5  | 1* | MISS  | 0     | eski→yeni kullanım: 6 5 1 |
|    9 |     5 | 6  | 5  | 1  | HIT   |       | eski→yeni kullanım: 6 1 5 |
|   10 |     1 | 6  | 5  | 1  | HIT   |       | eski→yeni kullanım: 6 5 1 |
|   11 |     3 | 3* | 5  | 1  | MISS  | 6     | eski→yeni kullanım: 5 1 3 |
|   12 |     1 | 3  | 5  | 1  | HIT   |       | eski→yeni kullanım: 5 3 1 |
|   13 |     4 | 3  | 4* | 1  | MISS  | 5     | eski→yeni kullanım: 3 1 4 |
|   14 |     2 | 2* | 4  | 1  | MISS  | 3     | eski→yeni kullanım: 1 4 2 |
|   15 |     1 | 2  | 4  | 1  | HIT   |       | eski→yeni kullanım: 4 2 1 |
|   16 |     0 | 2  | 0* | 1  | MISS  | 4     | eski→yeni kullanım: 2 1 0 |
|   17 |     5 | 5* | 0  | 1  | MISS  | 2     | eski→yeni kullanım: 1 0 5 |
|   18 |     2 | 5  | 0  | 2* | MISS  | 1     | eski→yeni kullanım: 0 5 2 |
|   19 |     0 | 5  | 0  | 2  | HIT   |       | eski→yeni kullanım: 5 2 0 |
|   20 |     5 | 5  | 0  | 2  | HIT   |       | eski→yeni kullanım: 2 0 5 |
+------+-------+----+----+----+-------+-------+---------------------------+
```
</details>

## Optimal (Belady MIN) (OPT) — 8 sayfa hatası

Kurban, bir sonraki kullanımı en uzakta olan (ya da hiç kullanılmayacak, ∞) sayfadır. Sağdaki sayılar sayfanın tekrar kullanılacağı adım numarasıdır.

```
Ref :  3  5  3  0  5  6  5  1  5  1  3  1  4  2  1  0  5  2  0  5
      -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
Ç0  :  3  3  3  3  3  3  3  3  3  3  3  3  4  2  2  2  2  2  2  2
Ç1  :  .  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5
Ç2  :  .  .  .  0  0  6  6  1  1  1  1  1  1  1  1  0  0  0  0  0
Hata:  F  F  ·  F  ·  F  ·  F  ·  ·  ·  ·  F  F  ·  F  ·  ·  ·  ·   (F = sayfa hatası)
```

<details><summary>Ayrıntılı adım tablosu</summary>

```
+------+-------+----+----+----+-------+-------+-----------------------------------------+
| Adım | Sayfa | Ç0 | Ç1 | Ç2 | Sonuç | Çıkan | Algoritma durumu                        |
+======+=======+====+====+====+=======+=======+=========================================+
|    1 |     3 | 3* | -  | -  | MISS  |       | sonraki kullanım (adım): 3→3            |
|    2 |     5 | 3  | 5* | -  | MISS  |       | sonraki kullanım (adım): 3→3 5→5        |
|    3 |     3 | 3  | 5  | -  | HIT   |       | sonraki kullanım (adım): 3→11 5→5       |
|    4 |     0 | 3  | 5  | 0* | MISS  |       | sonraki kullanım (adım): 3→11 5→5 0→16  |
|    5 |     5 | 3  | 5  | 0  | HIT   |       | sonraki kullanım (adım): 3→11 5→7 0→16  |
|    6 |     6 | 3  | 5  | 6* | MISS  | 0     | sonraki kullanım (adım): 3→11 5→7 6→∞   |
|    7 |     5 | 3  | 5  | 6  | HIT   |       | sonraki kullanım (adım): 3→11 5→9 6→∞   |
|    8 |     1 | 3  | 5  | 1* | MISS  | 6     | sonraki kullanım (adım): 3→11 5→9 1→10  |
|    9 |     5 | 3  | 5  | 1  | HIT   |       | sonraki kullanım (adım): 3→11 5→17 1→10 |
|   10 |     1 | 3  | 5  | 1  | HIT   |       | sonraki kullanım (adım): 3→11 5→17 1→12 |
|   11 |     3 | 3  | 5  | 1  | HIT   |       | sonraki kullanım (adım): 3→∞ 5→17 1→12  |
|   12 |     1 | 3  | 5  | 1  | HIT   |       | sonraki kullanım (adım): 3→∞ 5→17 1→15  |
|   13 |     4 | 4* | 5  | 1  | MISS  | 3     | sonraki kullanım (adım): 4→∞ 5→17 1→15  |
|   14 |     2 | 2* | 5  | 1  | MISS  | 4     | sonraki kullanım (adım): 2→18 5→17 1→15 |
|   15 |     1 | 2  | 5  | 1  | HIT   |       | sonraki kullanım (adım): 2→18 5→17 1→∞  |
|   16 |     0 | 2  | 5  | 0* | MISS  | 1     | sonraki kullanım (adım): 2→18 5→17 0→19 |
|   17 |     5 | 2  | 5  | 0  | HIT   |       | sonraki kullanım (adım): 2→18 5→20 0→19 |
|   18 |     2 | 2  | 5  | 0  | HIT   |       | sonraki kullanım (adım): 2→∞ 5→20 0→19  |
|   19 |     0 | 2  | 5  | 0  | HIT   |       | sonraki kullanım (adım): 2→∞ 5→20 0→∞   |
|   20 |     5 | 2  | 5  | 0  | HIT   |       | sonraki kullanım (adım): 2→∞ 5→∞ 0→∞    |
+------+-------+----+----+----+-------+-------+-----------------------------------------+
```
</details>

## Second Chance (Clock) (CLOCK) — 12 sayfa hatası

Çerçeveler dairesel listedir; `el` sıradaki adayı gösterir. Referans biti 1 olan sayfa ikinci şans alır (bit 0 yapılır, el ilerler); biti 0 olan ilk sayfa çıkarılır. `>` işareti elin konumudur.

```
Ref :  3  5  3  0  5  6  5  1  5  1  3  1  4  2  1  0  5  2  0  5
      -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
Ç0  :  3  3  3  3  3  6  6  6  6  6  3  3  3  3  1  1  1  2  2  2
Ç1  :  .  5  5  5  5  5  5  5  5  5  5  5  4  4  4  0  0  0  0  0
Ç2  :  .  .  .  0  0  0  0  1  1  1  1  1  1  2  2  2  5  5  5  5
Hata:  F  F  ·  F  ·  F  ·  F  ·  ·  F  ·  F  F  F  F  F  F  ·  ·   (F = sayfa hatası)
```

<details><summary>Ayrıntılı adım tablosu</summary>

```
+------+-------+----+----+----+-------+-------+----------------------------+
| Adım | Sayfa | Ç0 | Ç1 | Ç2 | Sonuç | Çıkan | Algoritma durumu           |
+======+=======+====+====+====+=======+=======+============================+
|    1 |     3 | 3* | -  | -  | MISS  |       | el=1  bitler: 3:1          |
|    2 |     5 | 3  | 5* | -  | MISS  |       | el=2  bitler: 3:1 5:1      |
|    3 |     3 | 3  | 5  | -  | HIT   |       | el=2  bitler: 3:1 5:1      |
|    4 |     0 | 3  | 5  | 0* | MISS  |       | el=0  bitler: >3:1 5:1 0:1 |
|    5 |     5 | 3  | 5  | 0  | HIT   |       | el=0  bitler: >3:1 5:1 0:1 |
|    6 |     6 | 6* | 5  | 0  | MISS  | 3     | el=1  bitler: 6:1 >5:0 0:0 |
|    7 |     5 | 6  | 5  | 0  | HIT   |       | el=1  bitler: 6:1 >5:1 0:0 |
|    8 |     1 | 6  | 5  | 1* | MISS  | 0     | el=0  bitler: >6:1 5:0 1:1 |
|    9 |     5 | 6  | 5  | 1  | HIT   |       | el=0  bitler: >6:1 5:1 1:1 |
|   10 |     1 | 6  | 5  | 1  | HIT   |       | el=0  bitler: >6:1 5:1 1:1 |
|   11 |     3 | 3* | 5  | 1  | MISS  | 6     | el=1  bitler: 3:1 >5:0 1:0 |
|   12 |     1 | 3  | 5  | 1  | HIT   |       | el=1  bitler: 3:1 >5:0 1:1 |
|   13 |     4 | 3  | 4* | 1  | MISS  | 5     | el=2  bitler: 3:1 4:1 >1:1 |
|   14 |     2 | 3  | 4  | 2* | MISS  | 1     | el=0  bitler: >3:0 4:0 2:1 |
|   15 |     1 | 1* | 4  | 2  | MISS  | 3     | el=1  bitler: 1:1 >4:0 2:1 |
|   16 |     0 | 1  | 0* | 2  | MISS  | 4     | el=2  bitler: 1:1 0:1 >2:1 |
|   17 |     5 | 1  | 0  | 5* | MISS  | 2     | el=0  bitler: >1:0 0:0 5:1 |
|   18 |     2 | 2* | 0  | 5  | MISS  | 1     | el=1  bitler: 2:1 >0:0 5:1 |
|   19 |     0 | 2  | 0  | 5  | HIT   |       | el=1  bitler: 2:1 >0:1 5:1 |
|   20 |     5 | 2  | 0  | 5  | HIT   |       | el=1  bitler: 2:1 >0:1 5:1 |
+------+-------+----+----+----+-------+-------+----------------------------+
```
</details>

## Least Frequently Used (LFU) — 10 sayfa hatası

Kurban, en az erişilen sayfadır (`sayfa×sayaç`). Eşitlikte en önce yüklenen çıkar. Sayaç, sayfa bellekten çıkınca sıfırlanır.

```
Ref :  3  5  3  0  5  6  5  1  5  1  3  1  4  2  1  0  5  2  0  5
      -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
Ç0  :  3  3  3  3  3  3  3  3  3  3  3  3  4  2  2  0  0  2  0  0
Ç1  :  .  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5  5
Ç2  :  .  .  .  0  0  6  6  1  1  1  1  1  1  1  1  1  1  1  1  1
Hata:  F  F  ·  F  ·  F  ·  F  ·  ·  ·  ·  F  F  ·  F  ·  F  F  ·   (F = sayfa hatası)
```

<details><summary>Ayrıntılı adım tablosu</summary>

```
+------+-------+----+----+----+-------+-------+--------------------+
| Adım | Sayfa | Ç0 | Ç1 | Ç2 | Sonuç | Çıkan | Algoritma durumu   |
+======+=======+====+====+====+=======+=======+====================+
|    1 |     3 | 3* | -  | -  | MISS  |       | sayaç: 3×1         |
|    2 |     5 | 3  | 5* | -  | MISS  |       | sayaç: 3×1 5×1     |
|    3 |     3 | 3  | 5  | -  | HIT   |       | sayaç: 3×2 5×1     |
|    4 |     0 | 3  | 5  | 0* | MISS  |       | sayaç: 3×2 5×1 0×1 |
|    5 |     5 | 3  | 5  | 0  | HIT   |       | sayaç: 3×2 5×2 0×1 |
|    6 |     6 | 3  | 5  | 6* | MISS  | 0     | sayaç: 3×2 5×2 6×1 |
|    7 |     5 | 3  | 5  | 6  | HIT   |       | sayaç: 3×2 5×3 6×1 |
|    8 |     1 | 3  | 5  | 1* | MISS  | 6     | sayaç: 3×2 5×3 1×1 |
|    9 |     5 | 3  | 5  | 1  | HIT   |       | sayaç: 3×2 5×4 1×1 |
|   10 |     1 | 3  | 5  | 1  | HIT   |       | sayaç: 3×2 5×4 1×2 |
|   11 |     3 | 3  | 5  | 1  | HIT   |       | sayaç: 3×3 5×4 1×2 |
|   12 |     1 | 3  | 5  | 1  | HIT   |       | sayaç: 3×3 5×4 1×3 |
|   13 |     4 | 4* | 5  | 1  | MISS  | 3     | sayaç: 4×1 5×4 1×3 |
|   14 |     2 | 2* | 5  | 1  | MISS  | 4     | sayaç: 2×1 5×4 1×3 |
|   15 |     1 | 2  | 5  | 1  | HIT   |       | sayaç: 2×1 5×4 1×4 |
|   16 |     0 | 0* | 5  | 1  | MISS  | 2     | sayaç: 0×1 5×4 1×4 |
|   17 |     5 | 0  | 5  | 1  | HIT   |       | sayaç: 0×1 5×5 1×4 |
|   18 |     2 | 2* | 5  | 1  | MISS  | 0     | sayaç: 2×1 5×5 1×4 |
|   19 |     0 | 0* | 5  | 1  | MISS  | 2     | sayaç: 0×1 5×5 1×4 |
|   20 |     5 | 0  | 5  | 1  | HIT   |       | sayaç: 0×1 5×6 1×4 |
+------+-------+----+----+----+-------+-------+--------------------+
```
</details>
