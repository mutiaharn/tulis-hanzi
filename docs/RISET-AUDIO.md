# Riset audio pengucapan — kosakata HSK 1

Tujuan: menyiapkan **bunyi cara membaca** untuk aplikasi Tulis Hanzi, dengan rencana fitur
*ketuk aksara / setelah satu aksara selesai ditulis → bunyinya*. Dokumen ini mencatat apa yang
**sudah diukur**, bukan perkiraan. Fokus: HSK 1 (150 kata, 178 aksara).

---

## Ringkasan keputusan (baca ini dulu)

| Pertanyaan | Jawaban terukur |
| --- | --- |
| Rekaman manusia untuk **kata** HSK 1 tersedia? | **Ya — 135 dari 150 kata**, diambil dari **133 berkas berbeda** (129 nama apa adanya + 4 lewat variasi nama berkas; 他/她 keduanya `tā` dan 做/坐 keduanya `zuò`, jadi satu rekaman dipakai dua kata) |
| Rekaman manusia untuk **per aksara**? | **Tidak layak** — hanya **9 dari 178 aksara** |
| Rekaman **per suku kata**? | Ada, 4.513 entri berbentuk pinyin di Wikimedia Commons |
| Suara konsisten? | **Ya, hampir seluruhnya satu penutur**: 132 berkas = *Wei Gao, Vion Nicolas*; 1 berkas penutur lain |
| Lisensi | **CC BY 2.0 fr** untuk 132 berkas (wajib cantumkan nama), **CC BY-SA 3.0** untuk 1 berkas |
| Ukuran | 1,81 MB asli (`.ogg`) → ± 1,4 MB setelah jadi MP3 (perkiraan dari 3 contoh terukur) |
| Siap dipakai sekarang? | Audio **kata**: siap untuk 133 kata. Audio **aksara**: perlu tambahan data *pinyin per aksara* dulu |

**Rekomendasi:** pakai rekaman manusia dari Commons sebagai bahan utama (nama penuturnya dicantumkan),
lalu tambal bagian yang kosong. Jangan pakai TTS sebagai bahan utama — lihat bagian 5.

---

## 1. Cara mengukur (bisa diulang kapan saja)

Semua angka di dokumen ini keluar dari skrip di folder `scripts/`, memakai API Wikimedia
(bukan dari ingatan, bukan dari daftar pihak ketiga):

| Perintah | Yang diukur |
| --- | --- |
| `python scripts/riset-audio.py` | rekaman per **kata** & per **aksara**, variasi nama berkas, penutur, lisensi, ukuran, dan tambalan dari rekaman **suku kata** |
| `python scripts/riset-audio-contoh.py` | format berkas: unduh 3 contoh, periksa codec, konversi ke MP3/M4A, ukur (butuh `ffmpeg`) |

Berkas hasil pengukuran (`riset-audio-*.json`, `riset-audio-contoh/`) **tidak** dimasukkan ke
repositori — semuanya bisa dibuat ulang dengan skrip di atas, dan sudah ada di `.gitignore`.

---

## 2. Hasil: rekaman per kata

Sumbernya rekaman pengucapan Mandarin yang dipakai proyek Wiktionary, disimpan di Wikimedia
Commons dengan nama berkas berpola **`Zh-<pinyin tanpa spasi, dengan tanda nada>.ogg`** —
contoh `Zh-wǒmen.ogg`, `Zh-píngguǒ.ogg`.

- **129 dari 150** kata HSK 1 punya rekaman dengan nama tepat sama dengan pinyin di aplikasi.
- **4 lagi** ditemukan setelah nama berkasnya dicoba divariasikan (karena di Commons spasi dan
  apostrof dihilangkan): `méi guānxi → Zh-méiguānxi.ogg`, `nǚ'ér → Zh-nǚér.ogg`,
  `Hànyǔ → Zh-hànyǔ.ogg`, `xià yǔ → Zh-xiàyǔ.ogg`.
- **Total: 135 dari 150 kata (90%)**, diambil dari **133 berkas berbeda**. Dua pengurangan itu
  masuk akal: 他 dan 她 sama-sama dibaca `tā`, dan 做 serta 坐 sama-sama dibaca `zuò` — jadi satu
  rekaman dipakai untuk dua kata, dan tidak ada gunanya mengunduh dua kali.
- Total ukuran asli: **1,81 MB**.

**15 kata yang belum punya rekaman** (perlu ditambal atau direkam sendiri):

谁 shéi · 不客气 bú kèqi · 小姐 xiǎojiě · 饭馆 fànguǎn · 说话 shuōhuà · 电脑 diànnǎo · 猫 māo ·
狗 gǒu · 打电话 dǎ diànhuà · 前面 qiánmiàn · 后面 hòumiàn · 火车站 huǒchēzhàn · 北京 Běijīng ·
中国 Zhōngguó · 出租车 chūzūchē

---

## 3. Hasil: rekaman per aksara — memang tidak tersedia

Dua cara dicoba, keduanya gagal:

1. Pola nama `Zh-<aksara>.ogg`: **0 dari 178** berkas ada.
2. Nama berkas audio yang **tercantum di halaman kamus Wiktionary tiap aksara** (cara yang
   seharusnya benar), lalu diperiksa keberadaannya di Commons: **9 dari 178 aksara** ada
   (contoh yang ada: 了, 冷, 喜, 子, 工, 怎, 打, 星).

Kesimpulan: **tidak bisa mengandalkan rekaman per aksara.** Bunyi per aksara harus disusun dari
rekaman **suku kata**, atau dibuat sendiri.

### Rekaman suku kata

Di Commons ada **4.513 berkas** berpola `Zh-<suku kata>.ogg` yang benar-benar berbentuk pinyin,
mis. `Zh-xǐ.ogg` (bacaan xǐ), `Zh-dǎ.ogg`.

Untuk 15 kata yang belum punya rekaman, dihitung suku kata yang dibutuhkan sebagai tambalan:
dari **29 suku kata**, **19 ada** dan **10 belum ada**: `bú, gǒu, huǒ, jiě, māo, nǎo, qi, shuí, shéi, zū`.

Artinya 7 dari 15 kata itu masih bisa dibunyikan aksara-per-aksara (饭馆, 说话, 打电话, 前面,
后面, 北京, 中国), sedangkan 8 kata lain belum lengkap (谁, 不客气, 小姐, 电脑, 猫, 狗,
火车站, 出租车).

---

## 4. Format berkas dan ukuran (ini yang menentukan bisa-tidaknya dipakai di iPhone)

Tiga berkas contoh diunduh dan diperiksa dengan `ffprobe`:

| Berkas | Codec asli | Sampel | Lama | Ukuran asli | → MP3 64k mono | → M4A 64k mono |
| --- | --- | --- | --- | --- | --- | --- |
| `Zh-wǒmen.ogg` | vorbis | 44.000 Hz mono | 1,05 s | 13.779 bita | 9.029 | 9.723 |
| `Zh-píngguǒ.ogg` | vorbis | 44.000 Hz mono | 1,35 s | 16.636 bita | 11.327 | 12.259 |
| `Zh-xǐ.ogg` | vorbis | 44.000 Hz mono | 1,05 s | 13.953 bita | 9.029 | 9.765 |

- Rata-rata: **9,8 KB** per berkas sebagai MP3, **10,6 KB** sebagai M4A.
- Perkiraan untuk 150 kata: **± 1,40 MB (MP3)** atau **± 1,51 MB (M4A)**.
- **Penting:** berkas Commons berformat Ogg Vorbis, dan **iOS/Safari tidak memutar Ogg Vorbis**.
  Karena aplikasi ini juga dipakai di iPhone, berkasnya **harus dikonversi** lebih dulu
  (ffmpeg sudah tersedia di mesin ini; konversi 3 contoh di atas nyata, bukan rencana).

---

## 5. Opsi yang dipertimbangkan

**Opsi A — rekaman manusia dari Commons (dipakai sebagai bahan utama).**
(+) Suara manusia asli, satu penutur (konsisten), lisensi jelas (CC BY 2.0 fr), ukuran kecil.
(−) 15 kata belum ada; tidak ada rekaman per aksara; wajib mencantumkan nama penutur.

**Opsi B — suara sintetis (TTS) dibuat sendiri dengan Piper.**
Model Mandarin yang tersedia dan statusnya (dibaca dari kartu model masing-masing, bukan dari ingatan):

| Model | Ukuran | Catatan lisensi |
| --- | --- | --- |
| `zh_CN-chaowen-medium` | 60,3 MB | dataset **CC0**, **tetapi** diturunkan dari suara Xiao Ya (non-komersial) → status tidak bersih |
| `zh_CN-huayan-medium` / `x_low` | 60,3 MB / 19,7 MB | dataset **"Unknown"** |
| `zh_CN-xiao_ya-medium` | 60,3 MB | **non-komersial** |

(+) Bisa membuat **semua** 150 kata dan semua suku kata, suara seragam.
(−) **Tidak ada satu pun model Mandarin Piper dengan lisensi yang benar-benar bersih**; kualitas
nada (tone) belum diperiksa; belum pernah dijalankan di mesin ini (perlu unduh ± 20–60 MB + programnya).

**Opsi C — gabungan (rekomendasi).**
Bahan utama rekaman manusia (135 kata), lalu bunyi per aksara diambil dari rekaman suku kata;
sisanya (8 kata & 10 suku kata) ditambal — entah dengan TTS, atau direkam sendiri oleh penutur.
Alasan memilih ini: bagian terbesar sudah tersedia dengan kualitas manusia dan lisensi yang jelas,
sementara bagian kosongnya kecil (± 10% kata) sehingga tidak perlu mengorbankan keseragaman suara
demi menutup semua lubang dengan suara sintetis.

---

## 6. Rancangan teknis fitur (belum dikerjakan)

1. **Tambah data `pinyin` per aksara** ke `app/data/hsk1.json`. Sekarang data hanya menyimpan pinyin
   **per kata** (`{"hanzi":"我们","pinyin":"wǒmen"}`), sedangkan fitur "ketuk aksara" butuh bacaan
   aksara itu. Ini sekaligus menyelesaikan masalah **aksara banyak bacaan**: 不 dibaca `bù`, tetapi
   dalam 不客气 dibaca `bú`; 一 bisa `yī/yí/yì`. Bacaan harus diambil dari kata yang sedang dibuka,
   bukan dari daftar aksara lepas.
2. **Nama berkas audio** mengikuti pinyin tanpa spasi (contoh `wǒmen`), sama seperti pola Commons
   supaya pengisian berikutnya gampang dicocokkan.
3. **Tombol audio hanya muncul kalau berkasnya ada.** Untuk 15 kata yang belum ada bunyinya,
   tombolnya tidak ditampilkan — lebih baik tidak ada tombol daripada tombol yang diam.
4. **Perilaku:** (a) satu aksara selesai ditulis dengan benar → bunyi aksara itu; (b) ketuk aksara
   di baris penunjuk aksara → bunyi aksara itu; (c) ketuk baris pinyin kata → bunyi kata utuh.
5. **Autoplay diblokir di HP.** Browser di HP hanya mengizinkan bunyi setelah ada sentuhan
   pengguna, jadi berkas audio perlu "dibuka" pada sentuhan pertama (mis. saat kata dipilih),
   bukan saat halaman dimuat.
6. **Hemat permintaan berkas:** 150 berkas kecil = 150 permintaan saat pertama dibuka. Pilihan yang
   lebih hemat: menggabungkan seluruh rekaman jadi **satu berkas** (audio *sprite*) plus tabel
   waktu mulai-tiap-bunyi; satu permintaan, tetap jalan offline, tetap bisa menunjuk bunyi tertentu.
   Ini juga membuat `sw.js` cukup menyimpan satu berkas besar.
7. **Offline:** berkas audio harus masuk daftar simpanan `sw.js`, dan versi cache harus ikut berubah
   (sudah otomatis lewat `scripts/build.py`) supaya HP tidak tertinggal versi lama.

---

## 7. Yang belum terverifikasi (jujur)

- **Kualitas pelafalan tiap rekaman belum didengar satu per satu.** Yang sudah dipastikan: berkasnya
  ada, penuturnya satu orang, lisensinya jelas. Apakah nada tiap kata benar menurut telinga penutur —
  belum diperiksa; ini pekerjaan yang paling tepat kamu lakukan (kamu pelajarnya).
- **TTS Piper belum dijalankan** di mesin ini; angka ukuran model di atas berasal dari daftar resmi
  Piper, bukan dari hasil jalan.
- **Belum diuji di iPhone/HP sungguhan** (termasuk pemutaran MP3/M4A di Safari dan perilaku autoplay).
- **15 kata + 10 suku kata masih kosong** — daftarnya di atas.
- Angka 4.513 inventaris suku kata menggambarkan **isi Commons saat pengukuran (5 Oktober 2026)**,
  bukan jaminan tetap.

---

## 8. Langkah berikutnya (kalau disetujui)

1. Tambahkan `pinyin` per aksara ke `app/data/hsk1.json` (178 aksara; sekaligus memeriksa bacaan
   yang berubah karena konteks).
2. Unduh 135 rekaman kata (133 berkas), konversi ke MP3/M4A dengan `ffmpeg`, gabung jadi satu berkas
   + tabel waktu.
3. Buat berkas `CREDITS-AUDIO.md` berisi nama penutur (*Wei Gao, Vion Nicolas*; *Sjors Provoost*
   untuk satu berkas), lisensi tiap berkas, dan tautan halaman Commons-nya — ini **kewajiban**
   lisensi CC BY, bukan pilihan.
4. Pasang tombol & perilaku bunyi (bagian 6), lalu uji lewat uji otomatis: jumlah berkas bunyi yang
   dimuat, bunyi yang benar untuk aksara yang diklik, dan tidak ada permintaan bunyi saat halaman dibuka.

---

© 2026 Mutiah Arinil Fayza Nusar
