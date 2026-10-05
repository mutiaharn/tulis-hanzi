# Tulis Hanzi

Aplikasi latihan menulis aksara Mandarin — **hanya** untuk itu, tanpa fitur lain supaya ringan
dan bisa langsung dipakai. Materi HSK 1 (150 kata), koreksi goresan langsung, jalan offline.

> **Dokumen:** [`docs/BRD.md`](docs/BRD.md) (kebutuhan & keputusan) ·
> [`docs/RANCANGAN-SISTEM.md`](docs/RANCANGAN-SISTEM.md) (cara kerjanya) ·
> [`docs/RISET-AUDIO.md`](docs/RISET-AUDIO.md) (rencana bunyi pengucapan) ·
> [`docs/CARA-PUSH-GITHUB.md`](docs/CARA-PUSH-GITHUB.md) (cara push & hosting) ·
> [`docs/hasil-uji.txt`](docs/hasil-uji.txt) (bukti pengujian)

Potret layar: [daftar kata](docs/tampilan-daftar.png) ·
[latihan menulis](docs/tampilan-latihan.png) ·
[aksara selesai](docs/tampilan-selesai.png) ·
[versi satu berkas](docs/satu-berkas-file-protocol.png)

---

## Cara memakai

### A. Dari internet (sudah tayang)
Buka **https://mutiaharn.github.io/tulis-hanzi/** di Chrome — bisa dari HP maupun laptop. Setelah
dibuka sekali, berkasnya tersimpan di perangkat dan aplikasi tetap jalan tanpa internet (lihat
bagian D untuk memasangnya sebagai ikon di layar utama).

### B. Paling cepat (tanpa server, satu berkas)
Buka **`dist/tulis-hanzi-satu-file.html`** — klik dua kali di komputer, atau kirim ke HP dan
buka dengan Chrome. Seluruh aplikasi + data ada di dalam berkas itu (416 KB), jadi jalan tanpa
internet dan tanpa pemasangan.

### C. Cara yang disarankan di laptop (bisa dipasang & offline)
```bat
python -m http.server 8777 --directory app
```
Lalu buka `http://127.0.0.1:8777` di Chrome.

### D. Memasang di HP (offline, ikon di layar utama)
Buka **https://mutiaharn.github.io/tulis-hanzi/** di Chrome HP, lalu menu ⋮ → **Tambahkan ke
layar utama**. Setelah dibuka sekali, aplikasi berjalan tanpa sinyal. Cara menerbitkan sendiri
untuk perubahan berikutnya: [`docs/CARA-PUSH-GITHUB.md`](docs/CARA-PUSH-GITHUB.md).

---

## Cara memakai aplikasinya

1. Pilih satu kata dari daftar (13 pelajaran bertema).
2. Jiplak aksara yang muncul di dalam kotak bergaris — **goresan yang salah tidak akan
   diterima**; kotak berkedip merah sebagai tanda, dan goresan salah itu tidak tertinggal di
   kanvas.
3. Titik-titik di bawah kotak menunjukkan berapa goresan yang sudah benar.
4. **Goresan yang sudah benar tetap terlihat** sampai kamu menekan **Hapus** atau pindah kata.
5. Kata beraksara banyak dikerjakan satu aksara pada satu waktu. Setelah satu aksara selesai,
   aplikasi berhenti dan menampilkan tombol **Aksara berikutnya** — jadi kamu bisa memeriksa
   tulisanmu dulu sebelum lanjut.
6. Tombol **Lihat contoh** memutar ulang contoh goresan **di dalam kanvas latihan itu sendiri**,
   tanpa menghapus tulisanmu. Contohnya menyingkir begitu kamu mulai menulis.

Salah dua kali pada goresan yang sama? Aplikasi menunjukkan kilasan goresan yang benar (tidak
dihitung sebagai nilai).

---

## Isi folder

| Folder/berkas | Isi |
| --- | --- |
| `app/` | aplikasinya (inilah yang diterbitkan ke internet) |
| `app/index.html` | dua layar: daftar kata + layar latihan |
| `app/js/app.js` | seluruh logika aplikasi (jelas dan berkomentar bahasa Indonesia) |
| `app/css/style.css` | tampilan |
| `app/data/hsk1.json` | 150 kata HSK 1 + 178 aksara + arti Indonesia (13 pelajaran) |
| `app/data/strokes.json` | data goresan 178 aksara (untuk koreksi & animasi) |
| `app/vendor/hanzi-writer.min.js` | pustaka Hanzi Writer (MIT) — disimpan lokal supaya bisa offline |
| `app/sw.js` | service worker: menyimpan berkas di HP supaya jalan tanpa internet |
| `dist/` | versi satu berkas hasil build |
| `docs/` | BRD, rancangan sistem, panduan push/hosting, hasil uji, potret layar |
| `scripts/` | skrip build, pengujian, dan alat ukur |
| `scripts/uji.py` | menjalankan 56 pemeriksaan otomatis, menyimpan buktinya ke `docs/hasil-uji.txt` |
| `scripts/uji-offline.py` | membuktikan pemakaian offline dengan cara yang ketat (cache HTTP dimatikan, jam nyata) |
| `scripts/uji-isian.py` | mengukur isian & contoh dari potret layar, piksel demi piksel |
| `scripts/hitung-tinta.py`, `scripts/banding-gambar.py` | menghitung dan membandingkan piksel tinta pada potret layar |
| `tests/` | uji otomatis + alat ukur + pembungkus pemotret layar |
| `.github/workflows/halaman.yml` | penerbitan otomatis ke GitHub Pages |

---

## Perintah yang sering dipakai

```bat
:: perbarui ikon + versi cache + versi satu berkas (jalankan setiap kali app/ berubah)
python scripts\build.py

:: jalan di laptop
python -m http.server 8777 --directory app

:: uji otomatis (butuh dua server; hasil tersimpan di docs/hasil-uji.txt)
start python -m http.server 8777 --directory app
start python -m http.server 8778 --directory .
python scripts\uji.py

:: uji pemakaian offline yang ketat (cache HTTP dimatikan; server 8777 harus hidup)
python scripts\uji-offline.py

:: bukti bug "goresan hilang sendiri" (membandingkan versi lama dan versi sekarang)
python scripts\buat-bukti-bug.py
:: lalu buka http://127.0.0.1:8778/tests/bukti-bug-resize.html

:: menghitung/membandingkan tinta pada potret layar (tanpa pustaka luar)
python scripts\hitung-tinta.py docs\tampilan-latihan.png 64 294 405 634
python scripts\banding-gambar.py docs\tampilan-lama.png docs\tampilan-baru.png
```

---

## Status pengujian

Pengujian otomatis menjalankan aplikasi asli di dalam iframe, lalu menekan kanvas memakai
koordinat yang diambil dari data goresan — jadi yang diuji benar-benar koreksi goresan, bukan
tiruan. Hasil terakhir: **56/56 lulus** (terinci di [`docs/hasil-uji.txt`](docs/hasil-uji.txt)).

Yang **belum** diverifikasi (jujur, agar tidak dianggap sudah beres):

- Arti Indonesia disusun dan diperiksa manual tanpa penutur asli; tiga arti yang paling tidak
  pas bisa diubah di `app/data/hsk1.json` lalu jalankan `python scripts\build.py`.
- iPhone/Safari belum pernah diuji (yang diuji Chrome di laptop dan Chrome headless).
- HP aslinya belum bisa diuji dari sini; yang diuji adalah tampilan pada ukuran layar HP
  (400 × 940) dan seluruh perilaku kanvas.
- Penerbitan ke GitHub Pages **sudah dijalankan dan diverifikasi** (5 Oktober 2026): workflow
  Actions sukses (job "terbit" selesai dalam 21 detik, commit `05681bb`), lalu halaman publiknya
  dibuka memakai Chrome headless dan **150 tombol kata benar-benar dirender** — bukan sekadar
  "laman membalas HTTP 200". Tautan: https://mutiaharn.github.io/tulis-hanzi/

---

## Bagaimana cara kerjanya (ringkas)

Rinciannya di [`docs/RANCANGAN-SISTEM.md`](docs/RANCANGAN-SISTEM.md); ini versi pendeknya:

- **Penilaian goresan** memakai pustaka Hanzi Writer, tetapi gambarnya dimatikan total — yang
  menilai tetap pustaka, yang menggambar aplikasi sendiri.
- **Yang terlihat di kanvas adalah bentuk asli goresan aksara** (bukan jalur jari). Aplikasi
  mengambil bentuk tertutup tiap goresan dari `app/data/strokes.json`, lalu membukanya sedikit demi
  sedikit mengikuti posisi jari lewat sebuah "koridor" selebar goresan itu.
- **Contoh arah goresan digambar di dalam kanvas latihan**, bukan di kotak terpisah, dengan animasi
  yang dijalankan sendiri oleh aplikasi — caranya begini supaya penilaian goresan tidak ikut batal.
- **Jalan tanpa internet** karena seluruh berkas (termasuk pustaka Hanzi Writer dan data goresan)
  disimpan di perangkat oleh `app/sw.js`; versi simpannya dihitung dari isi berkas saat build.
- **Versi satu berkas** (`dist/`) dibuat oleh `scripts/build.py` dengan memasukkan seluruh berkas
  ke dalam satu HTML, supaya aplikasi bisa dibuka tanpa server sama sekali.

---

## Rencana berikutnya: bunyi pengucapan

Sudah **diriset dan diukur**, belum dikerjakan: [`docs/RISET-AUDIO.md`](docs/RISET-AUDIO.md).
Ringkasnya — dari 150 kata HSK 1, **135 sudah punya rekaman pengucapan manusia** (133 berkas
berbeda) di Wikimedia Commons, hampir semuanya dari **satu penutur** (Wei Gao), lisensi
**CC BY 2.0 fr** sehingga
namanya **wajib dicantumkan**. Rekaman **per aksara hampir tidak tersedia** (9 dari 178), jadi
bunyi per aksara akan disusun dari rekaman suku kata. Berkasnya berformat Ogg dan **tidak bisa
diputar di iPhone**, jadi harus dikonversi dulu (ffmpeg). Rencananya: bunyi muncul saat satu
aksara selesai ditulis dengan benar dan saat aksara diketuk.

---

## Lisensi dan bahan pihak ketiga

- Pustaka **Hanzi Writer** — lisensi MIT, disimpan di `app/vendor/`.
- Data goresan aksara dari proyek Hanzi Writer (MIT).
- Daftar 150 kata mengikuti daftar resmi HSK 1; pinyin dan arti Indonesia disusun khusus untuk
  aplikasi ini.

© 2026 Mutiah Arinil Fayza Nusar
