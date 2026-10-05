# Rancangan Sistem — Tulis Hanzi

Dokumen pendamping `docs/BRD.md`. Isinya menjelaskan **bagaimana** aplikasi dibangun: susunan berkas, bentuk data, alur kerja, dan alasan tiap keputusan teknis — termasuk hal-hal yang mudah salah dan sudah dijaga di dalam kode.

---

## 1. Bentuk sistem secara keseluruhan

Tidak ada server dan tidak ada basis data. Seluruh aplikasi berjalan **di dalam browser HP** (sisi klien): kode, data kata, dan data goresan semuanya berkas statis yang diunduh sekali lalu disimpan oleh *service worker* di HP.

```
                          ┌──────────────────────────── HP pengguna ────────────────────────────┐
                          │                                                                     │
   (1) pembukaan pertama  │   Service Worker (sw.js)                                            │
   lewat tautan  ─────────┼──►  simpan semua berkas ke Cache Storage                            │
                          │         │                                                           │
                          │         ▼                                                           │
   (2) seterusnya,        │   Cache Storage  ──►  index.html + css + js + data (JSON)            │
   bahkan tanpa internet  │         │                                                           │
                          │         ▼                                                           │
                          │   Aplikasi (app.js)                                                 │
                          │     ├─ state: daftar kata, data goresan, posisi sekarang             │
                          │     ├─ layar daftar   → 150 tombol kata                             │
                          │     └─ layar latihan  → kanvas Hanzi Writer (mode kuis)             │
                          │                            ▲                                        │
                          │      sentuhan jari ────────┘  goresan dinilai di HP, tanpa jaringan │
                          └─────────────────────────────────────────────────────────────────────┘

   Di luar HP (sekali saja, saat membangun):
     daftar HSK 1  ─┐
     data goresan  ─┼─► scripts/  ─►  app/data/hsk1.json, app/data/strokes.json
     kode aplikasi ─┘                  └─► scripts/build.py ─► dist/tulis-hanzi-satu-file.html
```

Konsekuensi penting dari pilihan ini: tidak ada biaya server, tidak ada data pengguna yang bisa bocor, dan tidak ada yang bisa mati di sisi layanan. Sebaliknya, pembaruan materi berarti membangun ulang berkasnya, bukan menyunting basis data.

---

## 2. Susunan berkas

```
hanzi-tulis/
├── app/                          ← yang dipasang di HP
│   ├── index.html                ← kerangka dua layar (daftar & latihan)
│   ├── css/style.css             ← tampilan, seluruhnya lokal (tanpa font/CDN)
│   ├── js/app.js                 ← seluruh logika aplikasi + lapisan isian & contoh (± 700 baris, satu berkas)
│   ├── vendor/hanzi-writer.min.js ← pustaka Hanzi Writer 3.7.3 (MIT, 37 KB)
│   ├── data/hsk1.json            ← 150 kata: aksara, pinyin, arti, pelajaran (15 KB)
│   ├── data/strokes.json         ← goresan 178 aksara: 178 × (path bentuk + medians) (343 KB)
│   ├── sw.js                     ← service worker: simpan-semua untuk pemakaian offline
│   ├── manifest.webmanifest      ← nama, ikon, warna, mode layar penuh
│   └── icons/icon-192.png, icon-512.png
├── dist/tulis-hanzi-satu-file.html ← seluruh aplikasi dalam SATU berkas (432 KB)
├── scripts/build.py              ← membuat ikon + versi satu berkas
├── scripts/uji.py                ← menjalankan 56 pemeriksaan + menyimpan buktinya
├── scripts/uji-offline.py        ← uji pemakaian offline yang ketat (sertakan jam nyata)
├── scripts/uji-isian.py          ← mengukur isian & contoh dari potret layar (piksel)
├── tests/
│   ├── selftest.html             ← uji otomatis aplikasi asli (56 pemeriksaan)
│   ├── driver.html               ← pembantu memotret layar tertentu
│   ├── alat-ukur/                ← alat diagnosa: mengukur isian, lapisan, ukuran, struktur
│   └── periksa-tata.html         ← pemeriksa tata letak & ukuran kanvas
└── docs/                         ← BRD, rancangan sistem, bukti uji, tangkapan layar
```

Nama-nama di atas dipilih agar isi proyek bisa dijelaskan tanpa membuka kode: `data` berisi materi, `vendor` berisi buatan orang lain, `scripts` berisi alat pembangun.

---

## 3. Model data

Semuanya berbentuk JSON supaya bisa disunting dengan editor teks biasa maupun program.

### 3.1 `hsk1.json` — 150 kata

```json
{
  "meta": {
    "level": "HSK 1 (standar lama, 150 kata)",
    "sumber_daftar_kata": "github.com/drkameleon/complete-hsk-vocabulary (tag level old-1)",
    "sumber_pinyin_arti": "disusun manual untuk aplikasi ini; belum direview penutur asli",
    "jumlah_pelajaran": 13,
    "jumlah_kata": 150
  },
  "pelajaran": [
    {
      "id": 1,
      "tema": "Angka dasar",
      "kata": [
        { "hanzi": "一", "pinyin": "yī",   "arti": "satu" },
        { "hanzi": "二", "pinyin": "èr",   "arti": "dua" }
      ]
    }
  ]
}
```

Catatan penting soal sumbernya: daftar kata diambil dari repositori kosakata HSK untuk memastikan **150 katanya benar** (sudah dicocokkan satu per satu: tidak kurang, tidak lebih). Tetapi pinyin dan arti dari repositori itu **tidak dipakai**, karena entri acaknya sering bukan makna yang tepat untuk pelajar — contoh nyata yang ditemukan saat memeriksa: 上 tercatat `shǎng` ("used in 上声"), 听 tercatat `yǐn` ("smile, archaic"), 冷 tercatat sebagai nama marga. Untuk aplikasi belajar, arti seperti itu justru menyesatkan, jadi seluruh pinyin dan arti Indonesia disusun ulang secara manual.

### 3.2 `strokes.json` — bentuk dan urutan goresan

```json
{
  "字": {
    "strokes": ["M 350 571 Q 380 593 ... Z", "..."],   // 6 bentuk goresan (SVG path, grid 1024)
    "medians": [[[458,627],[392,631],"..."], "..."]     // 6 jalur tengah goresan (untuk penilaian)
  }
}
```

- `strokes` = bentuk tiap goresan, dipakai untuk menggambar dan menilai.
- `medians` = garis tengah tiap goresan; inilah yang dipakai pustaka untuk menilai apakah goresan pengguna "tepat di atas" goresan yang benar.

**Satuan koordinat (mudah salah):** grid 1024 × 1024, tetapi **sumbu Y mengarah ke atas** dan rentangnya -124…900. Artinya titik `y` kecil berada di **bawah** kanvas. Satu aksara `字` = 6 goresan, jadi 6 path dan 6 medians.

### 3.3 `state` di dalam aplikasi

```js
{
  hsk1, strokes,        // data yang sudah dimuat
  flat: [ { pel, wi, kata } × 150 ],   // 150 kata dalam satu baris, untuk navigasi
  idx,                  // kata yang sedang dibuka (0…149)
  ci,                   // aksara ke-berapa dari kata itu yang sedang ditulis
  writer, strokeIdx, total, size, busy,
  // tambahan untuk tampilan tinta & contoh (lihat 4.3):
  lapisan,              // { svg, isian, koridor, contoh, titik } — lapisan gambar milik aplikasi
  goresAktif,           // { median, kumulatif, total, panjang, setengah } goresan yang sedang ditulis
  tebal: {},            // ketebalan tiap goresan per aksara (dihitung sekali, lalu disimpan)
  generasi,             // penanda pemasangan kanvas (supaya lapisan yang telat tidak menimpa yang baru)
  contoh                // { jalan, animasi, jeda } — contoh arah goresan yang sedang diputar
}
```

Dibuat rata (`flat`) supaya tombol "Berikutnya" cukup menambah satu angka, tanpa memikirkan batas pelajaran.

---

## 4. Alur kerja utama

### 4.1 Pertama kali aplikasi dibuka
1. `index.html` dimuat → `app.js` meminta `data/hsk1.json` dan `data/strokes.json`.
2. `renderList()` membuat 13 blok pelajaran dan 150 tombol kata.
3. `sw.js` mendaftar, menyalin seluruh berkas ke Cache Storage.
4. Pembukaan berikutnya: berkas dilayani dari Cache Storage → tidak butuh jaringan.

### 4.2 Satu goresan ditulis (bagian paling penting)

```
jari menyentuh kanvas
   │  mousedown / touchstart          ← pustaka mendengarkan keduanya
   ▼
pustaka mencatat titik-titik goresan
   │  mousemove / touchmove           ← titik dikumpulkan selama jari bergerak
   ▼
jari diangkat
   │  mouseup / touchend (di dokumen)
   ▼
penilaian di dalam pustaka:
   • titik pengguna dikonversi ke grid 1024 (dengan pembalikan sumbu Y)
   • dibandingkan dengan `medians` goresan yang benar (jarak rata-rata, arah, kelonggaran)
   │
   ├── cocok  → `onCorrectStroke` dipanggil
   │              └─ aplikasi mengunci isian goresan itu (bentuk aslinya dinyatakan utuh)
   │                 dan menambah satu penanda goresan (satu titik menyala)
   │
   └── tidak  → `onMistake` dipanggil
                  ├─ aplikasi mengedipkan kotak merah (± 0,4 detik)
                  └─ aplikasi membuang gambar goresan yang ditolak dari kanvas
                     salah 2 kali → pustaka menunjukkan kilasan goresan yang benar (tidak dicatat)
```

Selama jari bergerak (sebelum diangkat), aplikasi sudah menjalankan isiannya sendiri — lihat 4.3. Pustaka hanya menilai; **pustaka tidak lagi menggambar apa pun** yang terlihat (`drawingColor` transparan), supaya tidak ada coretan mentah dan tidak ada pemudaran otomatis.

Catatan penting yang ditemukan lewat pengukuran: **pustaka tetap MENGGAMBAR goresan yang ditolak** dan membiarkan gambarnya di kanvas (diukur pada 3.7.3: masih terlihat 2 detik kemudian, bahkan setelah goresan berikutnya ditulis). Karena aturan produknya "goresan salah tidak diterima", gambar pustaka dimatikan sama sekali (transparan) dan isian milik aplikasi yang sedang berjalan dibuang saat goresan ditolak — jadi tidak ada tinta yang tertinggal. Diuji: "goresan salah tidak meninggalkan tinta di kanvas" LULUS (tinta=0).

Ketika `onCorrectStroke` yang terakhir dipanggil, `onComplete` berjalan → aplikasi menandai aksara itu selesai, menampilkan tombol **"Aksara berikutnya"**, dan **berhenti di situ** (tidak pindah sendiri). Bila itu aksara terakhir, muncul pesan "Selesai". Alasan berhenti: pemakai perlu waktu memeriksa tulisannya, dan tinta tidak boleh hilang tanpa dikehendaki.

### 4.3 Tampilan tinta & contoh arah goresan (dibuat ulang 5 Okt 2026)

Ini bagian yang menjawab dua permintaan pemilik produk: **contoh harus berada di dalam kanvas yang sama** dan **tulisan harus terisi mengikuti jari, bukan coretan acak**.

```
data goresan tiap aksara (app/data/strokes.json) berisi, untuk setiap goresan:
   • path    → BENTUK asli goresan (jalur tertutup, siap diisi warna)
   • medians → garis tengahnya (arah goresan yang benar)

lapisan aplikasi (#hw svg.lapisan-tinta, pointer-events:none — supaya sentuhan
tetap sampai ke pustaka) berisi:
   <path class="isian">    BENTUK asli goresan, ditampilkan sebagai tinta
   <path id="koridor">     "koridor": pita yang dibangun dari posisi jari
   <path class="contoh-arah">  jalur contoh (garis tengah, merah pucat)
   <circle class="ujung-contoh">  titik ujung contoh

jari bergerak (mousemove / touchmove)
   │  posisi jari diproyeksikan ke garis tengah goresan yang benar
   │  (titik terdekat pada garis tengah; ukuran "sudah ditempuh" hanya boleh bertambah)
   ▼
koridor dibangun ulang: gabungan potongan-potongan selebar ketebalan goresan itu
   │  (ketebalan diukur sekali per goresan dari jarak terjadi bentuk ke garis tengah)
   ▼
isian = BENTUK asli goresan dipotong oleh koridor (clip-path)
   → bagian aksara terbuka tepat sejauh jari berjalan; ujung depannya dibulatkan
   │
jari diangkat → pustaka menilai
   ├── benar → koridor dilepas: seluruh bentuk goresan itu tampil utuh dan tetap
   └── salah → isian yang sedang berjalan dibuang (tidak ada tinta tertinggal)

contoh arah goresan (diputar DI DALAM kanvas ini, bukan di kotak terpisah)
   • digambar sendiri oleh aplikasi dengan `stroke-dashoffset`, jadi penilaian
     goresan TIDAK ikut dibatalkan (kalau memakai animateStroke pustaka, kuis dibatalkan)
   • berjalan sendiri saat aksara dibuka (satu goresan berikutnya), atau seluruh
     aksara lewat tombol "Lihat contoh"
   • langsung menyingkir begitu pengguna mulai menulis
```

Dua hal ini membuat tampilan tidak berkedip: (a) yang terlihat selalu gambar milik aplikasi sendiri, bukan gambar pustaka yang muncul lalu dipudarkan; (b) ukuran "sudah ditempuh" tidak pernah mundur, jadi isian tidak berkedip balik saat jari bergerak maju-mundur kecil. Semuanya diukur: lihat `scripts/uji-isian.py` dan bagian "BUKTI ISIAN DAN CONTOH" di `docs/hasil-uji.txt`.

### 4.4 Membangun materi (di luar HP)
1. Ambil daftar 150 kata HSK 1 → dipakai sebagai pengunci kebenaran daftar kata.
2. Susun pinyin + arti Indonesia manual; periksa jumlahnya terhadap daftar itu (harus persis 150).
3. Kumpulkan goresan tiap aksara unik (178 aksara) → satu berkas `strokes.json`.
4. `scripts/build.py` membuat ikon PNG dan menyatukan semuanya jadi satu berkas HTML.

---

## 5. Struktur antarmuka

```
Layar daftar                          Layar latihan
┌───────────────────────────┐         ┌───────────────────────────┐
│ Tulis Hanzi (judul merah) │         │ ← Daftar kata             │
│ 01 ANGKA DASAR   (11 kata)│         │ Pelajaran 02 · Orang&…    │
│ [一][二][三][四][五]…      │  klik   │ wǒmen  (pinyin merah)     │
│ 02 ORANG & KATA GANTI     │ ──────► │ kami; kita                │
│ [人][我][你][他][她]…      │         │ [我][们]  ← aksara aktif   │
│ …13 pelajaran             │         │ ┌───────────────────────┐ │
└───────────────────────────┘         │ │      (kanvas 279–340) │ │
                                      │ │   template + 田字格    │ │
                                      │ └───────────────────────┘ │
                                      │ ●●○○○○○  ← penanda goresan │
                                      │ [Lihat contoh] [Hapus]    │
                                      │ [← Sebelumnya][Berikutnya]│
                                      └───────────────────────────┘
```

Dua layar saja, tanpa menu dan tanpa pengaturan. Tombol yang paling sering ditekan (Lihat contoh / Hapus) berada paling dekat dengan kanvas.

---

## 6. Keputusan teknis & alternatif yang ditolak

| Bagian | Yang dipakai | Alternatif yang ditolak & alasannya |
|---|---|---|
| Bentuk aplikasi | PWA (satu berkas HTML + service worker) | Flutter/Android asli: butuh 10–12 GB SDK, disk tersisa ± 11 GB. React Native: sama beratnya untuk kebutuhan sekecil ini |
| Menggambar & menilai aksara | Hanzi Writer 3.7.3 (MIT) | Menggambar manual di canvas: hanya bisa membandingkan gambar, sehingga goresan salah tetap lolos — persis masalah yang mau dihilangkan |
| Sumber data goresan | Hanzi Writer data, disimpan **lokal** (343 KB) | Memuat per aksara dari CDN seperti bawaan pustaka: gagal saat tanpa sinyal, dan lambat saat berganti aksara |
| Penilaian | Mode kuis pustaka (tolak/terima goresan) | Skor akurasi sendiri: menambah perhitungan & tampilan yang tidak diminta pengguna |
| Cara memuat data | Satu berkas `strokes.json` sekali muat | 178 permintaan berkas kecil: lebih lambat dan lebih rapuh saat luring |
| Tata letak kanvas | Satu kanvas besar + penunjuk aksara | Beberapa kanvas sejajar: kata 3 aksara di layar 360 px hanya menyisakan ± 100 px per kotak — terlalu kecil untuk jari |
| Kerangka aplikasi | JavaScript tanpa framework | React/Vue: menambah ± 100 KB dan langkah pembangunan tanpa manfaat untuk dua layar |
| Tema & font | Warna/font sistem + Noto Sans CJK bawaan HP | Font daring: melanggar syarat offline dan memperlambat tampil |
| Penyimpanan progres | Tidak ada | LocalStorage untuk progres: tidak diminta, dan menambah keadaan yang harus diurus |
| Pemasangan | `manifest.webmanifest` + `sw.js` | Minta pengguna memasang manual APK: tidak ada APK untuk aplikasi web |
| Konfigurasi kanvas | `showCharacter:false` + `drawingColor` transparan: template digambar sebagai **garis tepi** (`showOutline:true`, warna gading); pustaka hanya menilai, tidak menggambar | `showCharacter:true` (aksara samar penuh sejak awal): goresan yang sudah benar kelihatan "hilang", karena pustaka memudarkan tulisan pengguna sambil menampilkan aksara contohnya yang memang sudah tampak sejak awal. Inilah keluhan pemilik produk |
| Tampilan tinta | Lapisan gambar milik aplikasi (SVG di atas kanvas): BENTUK asli goresan dari `strokes.json` dipotong "koridor" yang dibangun dari posisi jari | Menggambar jalur jari apa adanya (bawaan pustaka): terlihat seperti coretan mentah, tidak seperti goresan aksara; dan gambar itu dipudarkan otomatis oleh pustaka |
| Letak contoh arah goresan | **Di dalam kanvas latihan yang sama** (kotak contoh terpisah dihapus), dianimasikan aplikasi sendiri dengan `stroke-dashoffset` | Kotak contoh terpisah di luar kanvas: pemilik produk minta contoh tersimulasi di tempat yang akan dicoret supaya arahnya jelas; memakai `animateStroke` pustaka: membatalkan kuis yang sedang berjalan (`cancelQuiz`) |
| Perpindahan aksara | Berhenti + tombol **"Aksara berikutnya"** | Pindah otomatis setelah 0,75 detik (versi awal): pemakai tidak sempat memeriksa tulisannya, dan kanvas tiba-tiba kosong seolah goresannya dihapus |
| Tinta goresan salah | Dibuang sendiri oleh aplikasi | Dibiarkan seperti bawaan pustaka: bertentangan dengan aturan "goresan salah tidak diterima" dan membingungkan |
| Pengubah ukuran kanvas | Tahan sampai selisih 16 px (batas aman tata letak), di atas itu baru dipasang ulang + ada pemberitahuan | Membangun ulang pada **setiap** perubahan (versi awal): memunculkan/menghilangkan scrollbar saja sudah menghapus tinta yang sudah ditulis |
| Versi cache service worker | Dihitung otomatis oleh `scripts/build.py` dari isi berkas (10 digit sidik jari SHA-256) | Menuliskan versi manual (`v1`, `v2`, …): mudah terlupa, akibatnya HP terus memakai berkas lama setelah aplikasi diperbarui |
| Penerbitan (hosting) | GitHub Pages lewat GitHub Actions (`.github/workflows/halaman.yml`), hanya folder `app/` yang diterbitkan | Menaruh seluruh repositori di akar situs: dokumen, skrip uji, dan berkas bukti ikut terbuka ke publik tanpa perlu; Netlify/Vercel: akun tambahan yang tidak dibutuhkan |

---

## 7. Titik rawan & penanganannya

Bagian ini mencatat hal-hal yang **sudah terbukti bermasalah** saat pembangunan, bukan dugaan.

**7.1 Ukuran kanvas untuk menilai ≠ ukuran kanvas yang tampil.**
Pustaka menilai goresan memakai ukuran kanvas yang diberikan saat pembuatan. Bila kotak yang tampil lebih kecil (misalnya karena kanvas diperas oleh kemunculan batang gulir), tinta akan muncul sedikit melenceng dari jari. Dua pengaman dipasang:
- lebar kanvas dihitung dari lebar dalam kartu (bukan dari bagian layar), dan kotak tidak boleh diperas (`flex:0 0 auto`);
- `scrollbar-gutter:stable` agar lebar tata letak tidak berubah saat kanvas muncul;
- jaring pengaman terakhir di `mountChar()`: bila ukuran tampil masih beda > 2 px, kanvas dipasang ulang sekali memakai ukuran nyata.
Bukti: sebelum diperbaiki 334 px (internal) vs 319 px (tampil); sesudahnya 279 px = 279 px.

**7.2 Batas 1 px pada kotak.**
Kotak bergaris memakai `box-shadow` sebagai bingkai, **bukan** `border`. Border 1 px ikut masuk hitungan tata letak sehingga kotak di dalamnya jadi 2 px lebih sempit daripada ukuran yang dipakai pustaka — sumber pergeseran yang sama seperti 7.1, hanya lebih kecil.

**7.3 Mengganti orientasi layar.** (diperbarui)
Pustaka menggambar sekali untuk ukuran tertentu, jadi saat ukuran **berubah besar** aplikasi memasang ulang kanvas aksara yang sedang ditulis (goresan aksara itu perlu diulang) dan memberi tahu pemakai dengan kalimat jelas. Ini disengaja: lebih baik daripada tinta melenceng. Tetapi pada versi awal, **setiap** perubahan ukuran — termasuk 20 px karena batang gulir muncul/hilang — ikut memasang ulang kanvas, dan itulah yang membuat tinta hilang tanpa dikehendaki. Perbaikannya:
- selisih sampai **16 px** diabaikan (kanvas tidak dipasang ulang);
- di atas 16 px barulah dipasang ulang, dengan pemberitahuan.

**7.4 Tampilan goresan yang ditolak.**
Diukur pada pustaka 3.7.3: setelah goresan ditolak, gambar goresan itu **tetap ada** di kanvas (opacity 1) dan masih terlihat 2 detik kemudian. Karena aplikasi mematikan gambar pustaka dan menggambar isiannya sendiri, yang perlu diurus hanya isian itu: isian yang sedang berjalan dibuang saat goresan ditolak. Garis tepi template dan isian goresan yang sudah benar tidak ikut terbuang.

**7.5 Service worker hanya jalan di alamat http/https.**
Karena itu aplikasi yang dibuka langsung dari berkas (`file://`) memakai versi satu berkas, dan pemasangan ke layar utama tidak tersedia di cara itu. Untuk hosting, rujukan di dalam `app/` semuanya relatif (`css/style.css`, `sw.js`), sehingga aplikasi tetap benar walau dipasang di subfolder seperti `https://namaakun.github.io/nama-repo/`.

**7.6 Pemasangan service worker butuh waktu NYATA (jebakan alat uji, bukan jebakan aplikasi).**
`--virtual-time-budget` hanya mempercepat timer halaman; pemasangan service worker dikerjakan proses browser. Akibatnya Chrome (headless) bisa keluar sebelum simpanan selesai ditulis, dan uji offline jadi lulus/gagal bergantung keberuntungan — padahal aplikasinya tidak berubah. Penanganannya di `scripts/uji-offline.py`: server uji punya alamat sengaja lambat (`/lambat?s=2.5`) yang diminta halaman pemantau berulang kali; selama permintaan itu belum dijawab, jam virtual Chrome menunggu, jadi browser tetap hidup dan pemasangan selesai. Hasilnya sekarang sama setiap kali dijalankan (tercatat di `docs/hasil-uji.txt`): 1 pendaftaran aktif, simpanan berisi **11 berkas**, dan aplikasi tetap terbuka tanpa server.

---

## 8. Cara memeriksa (bukan sekadar "kelihatannya jalan")

Uji otomatis menjalankan **aplikasi asli** di dalam iframe, lalu **menekan kanvas** memakai koordinat yang diambil dari `medians` data goresan. Jadi yang diuji adalah penilaian goresan sungguhan:

1. Jalankan dua server lokal dari akar proyek:
   ```bash
   python -m http.server 8777 --directory app      # aplikasi
   python -m http.server 8778 --directory .        # halaman uji (perlu akses ../app)
   ```
2. Buka `http://127.0.0.1:8778/tests/selftest.html` → **56 pemeriksaan**, hasilnya tercetak di halaman.

Perintah ringkas yang menjalankan semuanya dan menyimpan buktinya ke `docs/hasil-uji.txt`:

```bash
python scripts/uji.py
```

Untuk dijalankan tanpa membuka jendela (mis. saat memeriksa berkali-kali):

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --no-first-run \
  --user-data-dir="C:/Users/<nama>/AppData/Local/Temp/chrome-uji" \
  --virtual-time-budget=90000 --dump-dom \
  "http://127.0.0.1:8778/tests/selftest.html"
```

Tiga hal yang wajib diperhatikan saat membuat uji semacam ini (semuanya pernah membuat hasil uji menyesatkan):

- **`clientX`/`clientY` harus diberikan lewat opsi pembuatan `MouseEvent`.** Properti ini hanya-baca: menulis `e.clientX = 100` setelah event dibuat **diabaikan tanpa error**, sehingga semua event terkirim di titik (0,0) dan uji "gagal" padahal aplikasinya benar.
- **`iframe.contentDocument` harus diambil setelah iframe selesai memuat.** Diambil terlalu awal, yang didapat adalah dokumen `about:blank` yang kosong.
- **Hitungan gambar di DOM tidak boleh dijadikan satu-satunya bukti "tinta terlihat".** Animasi pustaka berjalan sendiri, jadi jumlah gambar pada satu detik tertentu naik-turun. Karena itu ada pemeriksa tingkat piksel: `scripts/hitung-tinta.py` (menghitung piksel gelap pada potret layar) dan `scripts/banding-gambar.py` (membandingkan dua potret piksel demi piksel, melaporkan letak perbedaannya). Keduanya membaca PNG sendiri tanpa pustaka luar, karena di mesin ini PIL/numpy tidak terpasang.

Selain itu `tests/periksa-tata.html` mengukur tata letak: apakah ada isi keluar layar, apakah ukuran kanvas internal sama dengan tampil, dan apakah ada teks tombol yang terpotong. Alat ukur lain ada di `tests/alat-ukur/` (memeriksa susunan lapisan kanvas, ukuran kanvas, dan struktur DOM) serta pembungkus pemotret layar di `tests/driver.html` dan `tests/driver-satu-berkas.html`.

### 8.1 Membuktikan bug "goresan hilang" dan perbaikannya

```bash
python scripts/buat-bukti-bug.py     # membuat salinan "versi lama" di tests/bukti-old/
# lalu buka http://127.0.0.1:8778/tests/bukti-bug-resize.html
```

Halaman itu menjalankan versi lama dan versi sekarang berdampingan, menulis satu goresan benar di keduanya, lalu memberi perlakuan yang sama. Hasil terukur:

| Perlakuan | Versi lama | Versi sekarang |
|---|---|---|
| Ukuran berubah sedikit (12 px, mis. scrollbar muncul) | kanvas dipasang ulang, tinta habis (0 goresan tersisa) | kanvas tidak dipasang ulang, tinta utuh (1 goresan tersisa) |
| Perubahan ukuran biasa tanpa lebar berubah (mis. menggulir di HP) | kanvas dipasang ulang, tinta habis | kanvas tidak dipasang ulang, tinta utuh |
| Ukuran berubah besar (80 px, mis. HP diputar) | dipasang ulang | dipasang ulang juga — disengaja, dengan pemberitahuan |
| Piksel tinta di potret layar: tanpa goresan vs aksara lengkap (7 goresan) | — | 0 px vs **11.818 px** (10,3% kanvas) |

Dua catatan kejujuran:

- Jumlah gambar tinta pada **satu detik tertentu** tidak bisa dipakai sebagai bukti, karena animasi pustaka belum tentu selesai saat itu — sudah terbukti angkanya berubah antar-jalan. Karena itu bukti "tinta terlihat" diambil dari **piksel potret layar** (`scripts/hitung-tinta.py`), bukan dari hitungan DOM.
- Sebab kanvas-dipasang-ulang pada versi lama sudah terbukti dan diperbaiki. Sebab kedua (pengaturan `showCharacter`) dinyatakan **berdasarkan isi kode pustaka** (`endUserStroke` memudarkan goresan pengguna; goresan aksara yang menggantikannya tampil dalam warna `strokeColor`) dan pengamatan lapisan kanvas lewat `tests/alat-ukur/diagnosa-kanvas.html` (menampilkan warna dan lebar setiap lapisan yang terlihat), bukan dari satu potret. Karena itu perbaikannya digambarkan sebagai "mengikuti cara pustaka yang benar", bukan sebagai angka.

---

## 9. Rencana teknis lanjutan

| Langkah | Perubahan yang diperlukan |
|---|---|
| Menambah HSK 2 (150 kata) | Tambah pelajaran ke `hsk1.json` (atau berkas `hsk2.json`), tambah goresan aksara baru ke `strokes.json`, jalankan `scripts/build.py` |
| Memasang di HP dari tautan | Terbitkan folder `app/` ke GitHub Pages (alamat https) → buka di Chrome HP → "Tambahkan ke layar utama" |
| Audio pelafalan | Berkas suara lokal per kata + satu tombol; tetap offline |
| Daftar kata yang sering salah | Tambah penghitung di LocalStorage dan layar ketiga; tidak mengubah struktur data yang ada |
| Uji di iPhone | Perlu perangkat/emulator iOS; pemakaian event sentuh pustaka sudah sesuai standar |
