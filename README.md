# Tulis Hanzi

Aplikasi latihan menulis aksara Mandarin — **hanya** untuk itu, tanpa fitur lain supaya ringan
dan bisa langsung dipakai. Materi HSK 1 (150 kata), koreksi goresan langsung, jalan offline.

> **Dokumen:** [`docs/BRD.md`](docs/BRD.md) (kebutuhan & keputusan) ·
> [`docs/RANCANGAN-SISTEM.md`](docs/RANCANGAN-SISTEM.md) (cara kerjanya) ·
> [`docs/CARA-PUSH-GITHUB.md`](docs/CARA-PUSH-GITHUB.md) (cara push & hosting) ·
> [`docs/hasil-uji.txt`](docs/hasil-uji.txt) (bukti pengujian)

Potret layar: [daftar kata](docs/tampilan-daftar.png) ·
[latihan menulis](docs/tampilan-latihan.png) ·
[aksara selesai](docs/tampilan-selesai.png) ·
[versi satu berkas](docs/satu-berkas-file-protocol.png)

---

## Cara memakai

### A. Paling cepat (tanpa server, satu berkas)
Buka **`dist/tulis-hanzi-satu-file.html`** — klik dua kali di komputer, atau kirim ke HP dan
buka dengan Chrome. Seluruh aplikasi + data ada di dalam berkas itu (416 KB), jadi jalan tanpa
internet dan tanpa pemasangan.

### B. Cara yang disarankan di laptop (bisa dipasang & offline)
```bat
python -m http.server 8777 --directory app
```
Lalu buka `http://127.0.0.1:8777` di Chrome.

### C. Memasang di HP (offline, ikon di layar utama)
Terbitkan isi folder `app/` ke GitHub Pages (langkah lengkapnya di
[`docs/CARA-PUSH-GITHUB.md`](docs/CARA-PUSH-GITHUB.md)), buka alamatnya di Chrome HP, lalu
menu ⋮ → **Tambahkan ke layar utama**. Setelah dibuka sekali, aplikasi berjalan tanpa sinyal.

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
6. Tombol **Lihat contoh** membuka kotak kecil berisi animasi goresan yang sedang dibutuhkan.
   Ketuk kotaknya untuk memutar ulang animasinya.

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
- Penerbitan ke GitHub Pages belum pernah dijalankan sungguhan (belum ada login GitHub di
  mesin ini). Alur dan berkasnya sudah siap; kegagalan pertama paling mungkin soal
  penyalaan Pages di langkah 4 panduan, dan itu ada di bagian "kalau ada masalah".

---

## Lisensi dan bahan pihak ketiga

- Pustaka **Hanzi Writer** — lisensi MIT, disimpan di `app/vendor/`.
- Data goresan aksara dari proyek Hanzi Writer (MIT).
- Daftar 150 kata mengikuti daftar resmi HSK 1; pinyin dan arti Indonesia disusun khusus untuk
  aplikasi ini.

© 2026 Mutiah Arinil Fayza Nusar
