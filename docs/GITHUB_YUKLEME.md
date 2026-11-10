# GitHub'a yükleme

Bu klasör hazır bir git deposudur: modül bazlı commit'ler, her bileşen için bir `feature/*` dalı ve
`--no-ff` merge'ler içerir. Geçmişi görmek için:

```bash
git log --graph --oneline --all
```

## Yöntem A — kendi hesabınızda yeni depo (önerilen)

Eski grup deposunda başkalarının commit'leri olduğu için tek kişilik teslimde kendi deponuz daha temizdir.

1. GitHub → **New repository** → ad: `sayfa-degistirme-simulatoru`, **README eklemeden** oluşturun.
   Gizli (private) yaparsanız: Settings → Collaborators → hocayı ekleyin.
2. Proje klasöründe terminal:

```bash
git remote add origin https://github.com/<kullanici-adiniz>/sayfa-degistirme-simulatoru.git
git push -u origin main
git push origin --all
```

3. GitHub'da **Actions** sekmesinde "testler" iş akışının yeşil olduğunu görün (ilk push'tan 1–2 dk sonra).

## Yöntem B — mevcut depoya yazmak

Depo sizin hesabınızdaysa ve eski içeriği değiştirmek istiyorsanız:

```bash
git remote add origin https://github.com/<sahip>/sayfa-degistirme-simulatoru.git
git push -u origin main --force
git push origin --all
```

`--force` uzak `main`'deki eski geçmişi siler; yalnızca depo size aitse ve bunu istiyorsanız kullanın.

## Commit kimliği

Commit'ler `Sabina Gasimova <202303011138@dogus.edu.tr>` adına kayıtlıdır. GitHub profilinizde
görünmesi için bu e-postayı GitHub → Settings → Emails bölümüne ekleyin. Sonraki commit'leriniz için:

```bash
git config user.name "Sabina Gasimova"
git config user.email "202303011138@dogus.edu.tr"
```

## Sonraki çalışma (final için)

```bash
git checkout -b feature/aging
# ... geliştirme ...
git commit -am "Aging algoritması ve testleri"
git checkout main && git merge --no-ff feature/aging
git push origin main feature/aging
```
