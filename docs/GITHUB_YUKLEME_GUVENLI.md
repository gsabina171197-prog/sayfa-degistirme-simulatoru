# GitHub yayımlama — güvenli yol

Bu ZIP içinde zaten `.git` klasörü, `main` ve `feature/*` dalları mevcuttur. `git init` yapmayın, `.git` klasörünü silmeyin.

1. GitHub'da `sayfa-degistirme-simulatoru` adında boş depo oluşturun. **Initialize with README** seçeneğini işaretlemeyin.
2. ZIP'i tüm dosyalarla çıkarıp terminali `main.py` dosyasının olduğu klasörde açın.
3. Aşağıdaki komutlarda `KULLANICI_ADI` yerine **kendi gerçek GitHub kullanıcı adınızı** yazın.

```bash
git status
git log --oneline -5
git remote -v
git remote add origin https://github.com/KULLANICI_ADI/sayfa-degistirme-simulatoru.git
# 'origin already exists' görürseniz bunun yerine:
# git remote set-url origin https://github.com/KULLANICI_ADI/sayfa-degistirme-simulatoru.git
git push -u origin main
git push origin --all
git push origin --tags
```

4. GitHub Actions `tests` iş akışını kontrol edin; **kontrol etmeden başarılı olduğunu iddia etmeyin**.
5. Son olarak hoca ile gerçek depo bağlantısını paylaşın. Özel depo ise hocanın erişimi için Collaborators izni gerekecektir.

**Uyarı:** `git push --force` kullanmayın. ZIP'i GitHub web arayüzünden dosya ekleyerek yüklemek yerel commit/branch geçmişini taşımaz; terminal üzerinden push edin.
