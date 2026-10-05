# Cara push ke GitHub dan menerbitkan aplikasinya (hosting)

> **Catatan (5 Oktober 2026): penerbitan pertama SUDAH dikerjakan.** Aplikasinya tayang di
> https://mutiaharn.github.io/tulis-hanzi/ — repo `mutiaharn/tulis-hanzi`, Pages sumber
> "GitHub Actions", commit `05681bb`. Untuk **pembaruan berikutnya** cukup langkah 6
> (build → commit → push). Langkah 1–4 hanya perlu diulang kalau berganti akun/repositori
> atau kalau Pages dimatikan.

Panduan ini langkah demi langkah, dari folder di laptop sampai aplikasi bisa dibuka di HP
lewat alamat internet. Semua perintah ditulis untuk **Command Prompt (cmd.exe)** — kalau kamu
memakai Git Bash atau PowerShell, perintahnya sama kecuali cara menulis alamat folder
(di Git Bash: `cd /c/Documents/hanzi-tulis`).

Ringkasnya lima langkah:

1. Buat repositori kosong di GitHub (papan di web).
2. Siapkan repositori di laptop dan kirim isinya (push).
3. Nyalakan GitHub Pages (sekali saja).
4. Buka alamat situsnya, lalu pasang di layar utama HP.
5. Setiap ada perubahan: build → commit → push.

---

## 0. Apa yang sudah disiapkan di folder ini

| Berkas/folder | Gunanya |
| --- | --- |
| `app/` | **aplikasinya sendiri** — inilah yang diterbitkan ke internet |
| `.github/workflows/halaman.yml` | resep otomatis: setiap push, isi `app/` diterbitkan ke GitHub Pages |
| `dist/tulis-hanzi-satu-file.html` | versi satu berkas, bisa dibuka tanpa internet/hosting (cadangan) |
| `docs/` | dokumen (BRD, rancangan sistem, hasil uji) — tidak ikut diterbitkan |
| `scripts/` | skrip build dan pengujian |
| `tests/` | uji otomatis dan alat ukur — tidak ikut diterbitkan |

Penting: semua rujukan di dalam `app/` memakai **alamat relatif** (contoh `css/style.css`,
`sw.js`), bukan alamat berawalan `/`. Karena itu aplikasi tetap jalan walau dipasang di
subfolder seperti `https://namaakun.github.io/tulis-hanzi/`. Ini sudah diperiksa.

---

## 1. Yang perlu disiapkan

1. Akun GitHub (punyamu: `mutiaharn`).
2. Git sudah terpasang di laptop (sudah, karena proyek ini dikerjakan dengan git).
   Periksa dengan:
   ```bat
   git --version
   git config --global user.name
   git config --global user.email
   ```
   Kalau `user.name`/`user.email` kosong, isi sekali saja:
   ```bat
   git config --global user.name "Mutiah Arinil Fayza Nusar"
   git config --global user.email "mutiaharinil@gmail.com"
   ```
3. GitHub CLI (`gh`) **tidak wajib**. Panduan ini memakai perintah `git` biasa.

---

## 2. Buat repositori kosong di GitHub

1. Buka https://github.com/new (dalam keadaan sudah login).
2. Isi:
   - **Repository name**: `tulis-hanzi`
   - **Description**: `Latihan menulis aksara Mandarin HSK 1 — PWA ringan, bisa offline`
   - **Public** (wajib untuk GitHub Pages gratis). Jangan centang **Private**.
   - **JANGAN** centang "Add a README file", "Add .gitignore", atau "Choose a license"
     — biarkan benar-benar kosong supaya tidak bentrok saat push pertama.
3. Klik **Create repository**. Halaman berikutnya menampilkan alamat repositori, contohnya:
   `https://github.com/mutiaharn/tulis-hanzi.git` — alamat ini dipakai di langkah 3.

---

## 3. Siapkan repositori di laptop lalu push

Buka **Command Prompt**, lalu jalankan perintah berikut satu blok demi satu blok.

```bat
cd /d C:\Documents\hanzi-tulis
```

**a. Perbarui dulu berkas hasil build** (ikon, versi cache service worker, versi satu berkas):

```bat
python scripts\build.py
```

Keluarannya seperti: `ikon : app\icons\icon-192.png 192 x 192`,
`cache : var CACHE = 'tulis-hanzi-xxxxxxxxxx';`, `satu berkas: dist\tulis-hanzi-satu-file.html 416 KB`.

> Jalankan ini **setiap kali** kamu mengubah apa pun di dalam `app/`, sebelum commit.
> Skrip itu menghitung ulang versi cache service worker dari isi berkas, sehingga HP yang
> sudah pernah membuka aplikasi akan mengambil versi baru, bukan simpanan lama.

**b. Nyalakan repositori git dan buat catatan pertama:**

```bat
git init -b main
git add .
git status
```

`git status` memperlihatkan daftar berkas yang akan dikirim. Periksa sebentar: yang muncul
harusnya `app/`, `dist/`, `docs/`, `scripts/`, `tests/`, `.github/`, `.gitignore`, `README.md`.
Folder `tests/bukti-old/` (salinan untuk pembuktian bug) tidak akan muncul karena sudah
didaftarkan di `.gitignore`.

```bat
git commit -m "Tulis Hanzi: aplikasi latihan menulis aksara Mandarin HSK 1"
```

**c. Hubungkan ke repositori GitHub lalu kirim:**

```bat
git remote add origin https://github.com/mutiaharn/tulis-hanzi.git
git push -u origin main
```

Saat push pertama, Git Credential Manager akan membuka jendela masuk GitHub di browser —
pilih akun `mutiaharn` dan izinkan. Setelah itu, push berikutnya tidak akan bertanya lagi.

**d. Periksa hasilnya** (tanpa membuka browser):

```bat
git ls-remote --heads origin
```

Kalau muncul baris berisi `refs/heads/main`, isi folder sudah berhasil terkirim.

---

## 4. Nyalakan GitHub Pages (sekali saja)

1. Buka `https://github.com/mutiaharn/tulis-hanzi/settings/pages`.
2. Pada **Build and deployment → Source**, pilih **GitHub Actions**
   (bukan "Deploy from a branch").
3. Tidak perlu memilih branch atau folder.

Setelah itu, setiap push ke `main` otomatis menerbitkan isi `app/`. Prosesnya bisa dilihat di
tab **Actions** repositori (klik workflow "Terbitkan aplikasi ke GitHub Pages"). Selesai
biasanya 30–90 detik.

> Kalau kamu menyalakan Pages **setelah** push pertama, jalankan ulang penerbitannya:
> tab **Actions** → pilih workflow → tombol **Re-run all jobs**. Tidak perlu push ulang.

Kalau tab Actions kosong (workflow belum terdeteksi), jalankan:

```bat
git commit --allow-empty -m "Picu penerbitan ulang"
git push
```

---

## 5. Buka alamat situsnya dan pasang di HP

Alamat situsmu:

```
https://mutiaharn.github.io/tulis-hanzi/
```

Cara memasang di layar utama HP (Chrome Android):
1. Buka alamat di atas dengan **Chrome**.
2. Tekan menu titik tiga (kanan atas) → **Add to Home screen / Tambahkan ke layar utama**.
3. Beri nama "Tulis Hanzi" → tambahkan.

Setelah itu aplikasi muncul seperti aplikasi biasa, dan **tetap bisa dibuka walau tidak ada
internet**, karena berkasnya sudah disimpan di HP oleh service worker.

> Di iPhone: buka di **Safari** → tombol Share → **Add to Home Screen**.

---

## 6. Cara memperbarui aplikasi nanti

Setiap kali kamu mengubah sesuatu (misalnya menambah kata HSK 2), urutannya:

```bat
cd /d C:\Documents\hanzi-tulis
python scripts\build.py
git add .
git commit -m "Tambah data kata HSK 2"
git push
```

Tunggu 1–2 menit, lalu buka aplikasinya di HP. Kalau masih tampil versi lama:
tutup aplikasi dari daftar aplikasi yang terbuka, lalu buka lagi. Versi cache sudah berubah
sendiri (dihitung dari isi berkas), jadi HP akan mengambil berkas baru saat dibuka.

---

## 7. Menguji di laptop sebelum dikirim

```bat
cd /d C:\Documents\hanzi-tulis
python -m http.server 8777 --directory app
```

Lalu buka http://127.0.0.1:8777/ di Chrome. Tekan `Ctrl+C` di jendela Command Prompt untuk
menghentikannya.

Menjalankan seluruh pengujian otomatis (butuh dua server, karena uji dijalankan dari halaman
uji yang terpisah):

```bat
start python -m http.server 8777 --directory app
start python -m http.server 8778 --directory .
python scripts\uji.py
```

Hasilnya tersimpan di `docs/hasil-uji.txt`. Yang diharapkan: `RINGKASAN: 56/56 lulus`.

---

## 8. Cadangan tanpa hosting: versi satu berkas

`dist/tulis-hanzi-satu-file.html` berisi seluruh aplikasi + data dalam satu berkas (416 KB).
Kirim berkas itu ke HP lewat WhatsApp/kabel, lalu buka dengan Chrome — aplikasinya jalan
tanpa internet dan tanpa server sama sekali. Berguna kalau kuota sedang tipis atau hosting
belum siap.

---

## 9. Kalau ada masalah

| Gejala | Sebab dan solusinya |
| --- | --- |
| `fatal: not a git repository` | Perintah dijalankan di folder yang salah. Jalankan `cd /d C:\Documents\hanzi-tulis` dulu. |
| `remote: Repository not found` | Nama akun/repositori di alamat salah, atau repositori belum dibuat di web. Periksa di halaman GitHub-nya. |
| `! [rejected] main -> main (fetch first)` | Di GitHub sudah ada berkas yang belum ada di laptop. Jalankan `git pull --rebase origin main` lalu `git push`. |
| Push meminta sandi berulang | Pakai jendela Git Credential Manager yang muncul, bukan mengetik sandi akun. Kalau macet: `git config --global credential.helper manager`. |
| Actions merah, pesan `Get Pages site failed` | Pages belum dinyalakan. Ulangi langkah 4, lalu **Re-run all jobs**. |
| Situs tampil 404 setelah Actions hijau | Tunggu 1–2 menit (penyebaran berkas), lalu buka ulang di jendela penyamaran (`Ctrl+Shift+N`). Periksa juga alamatnya berakhiran `/` . |
| Aplikasi masih versi lama di HP | Tutup aplikasi dari daftar aplikasi terbuka, buka lagi. Pastikan `python scripts\build.py` dijalankan sebelum commit. |
| Ikon di layar utama tidak berubah | Hapus pintasan lama, lalu pasang ulang dari Chrome. |

**Alternatif kalau Actions tidak bisa dipakai** (mis. kuota Actions habis atau kamu lebih suka
cara tanpa otomatis):

1. Di `Settings → Pages → Source`, pilih **Deploy from a branch**.
2. Pindahkan isi `app/` ke akar repositori, supaya GitHub bisa menerbitkannya:
   ```bat
   git mv app/index.html app/css app/js app/data app/vendor app/icons app/sw.js app/manifest.webmanifest .
   rmdir app
   git add -A
   git commit -m "Pindahkan aplikasi ke akar repositori untuk hosting"
   git push
   ```
   Perhatikan ada titik (`.`) di akhir perintah `git mv` itu — artinya "ke folder sekarang".
3. Tunggu satu menit dan buka alamat yang sama. Alamat berkas aplikasi menjadi
   `https://mutiaharn.github.io/tulis-hanzi/index.html`.

Kalau memilih cara alternatif ini, perintah uji di langkah 7 berubah menjadi
`python -m http.server 8777` (tanpa `--directory app`).

---

## 10. Catatan penting

- **Repositori ini publik.** Jangan pernah menyimpan sandi, token, nomor HP, atau data
  pribadi di dalamnya. Aplikasi ini memang tidak butuh data pribadi apa pun.
- **Tidak ada biaya.** GitHub Pages gratis untuk repositori publik, dan kuota Actions jauh
  lebih besar daripada kebutuhan proyek ini (satu penerbitan hanya beberapa detik).
- **Nama berkas berpengaruh.** GitHub Pages membedakan huruf besar/kecil
  (`app/JS/app.js` ≠ `app/js/app.js`). Jangan mengubah nama berkas hanya demi gaya penulisan.
- **Alamat folder `app/` di berkas lain** (`scripts/`, `tests/`) memakai alamat relatif, jadi
  memindahkan folder aplikasi mengharuskan penyesuaian alamat di skrip uji. Kalau hanya
  menambah kata atau memperbaiki tampilan, tidak ada yang perlu disesuaikan.
- **Lisensi**: aplikasi ini memakai pustaka **Hanzi Writer** (lisensi MIT) dan data goresan
  dari proyek yang sama. Kalau kamu ingin memberi lisensi pada proyekmu, berkas `LICENSE`
  boleh ditambahkan, tetapi tidak wajib.
