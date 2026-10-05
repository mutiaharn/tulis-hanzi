# BRD — Tulis Hanzi
### Aplikasi latihan menulis aksara Mandarin (HSK 1)

| | |
|---|---|
| **Nama produk** | Tulis Hanzi |
| **Jenis** | Aplikasi web yang bisa dipasang di HP (PWA), tanpa server |
| **Pemilik produk** | Mutiah Arinil Fayza Nusar |
| **Versi dokumen** | 1.0 |
| **Status** | Sudah dibangun & terverifikasi (bukan rencana di atas kertas) |
| **Tanggal** | 5 Oktober 2026 |

---

## 1. Ringkasan

Tulis Hanzi adalah aplikasi yang **hanya** melakukan satu hal: melatih tangan menulis aksara Mandarin. Pengguna memilih satu kata dari daftar HSK 1, lalu menjiplak setiap aksaranya di atas template bergaris 田字格. Goresan yang salah **tidak diterima** — jadi urutan dan bentuk goresan yang benar terbentuk sejak awal, bukan sekadar dilihat. Tidak ada fitur lain: tanpa akun, tanpa kuis pilihan ganda, tanpa angka skor, tanpa koneksi internet.

Alasan memilih bentuk sesempit ini: aplikasi latihan menulis paling sering gagal karena berat dan penuh fitur, bukan karena kurang fitur. Target pemakaiannya adalah "buka HP, tulis 5 menit, tutup" — jadi seluruh aplikasi harus termuat dalam hitungan detik dan tetap jalan saat tidak ada sinyal (mis. di kampus, di angkot).

---

## 2. Latar belakang & masalah

Belajar menulis aksara Mandarin berbeda dari belajar membaca. Membaca cukup mengenali bentuk; menulis menuntut otot tangan mengikuti **urutan goresan** yang benar. Belajar dari video atau buku punya satu kelemahan mendasar: tidak ada yang memberi tahu saat tangan kita salah. Kesalahan yang terulang lalu mengeras jadi kebiasaan — dan sulit diperbaiki setelah terbentuk.

Masalah spesifik yang mau diselesaikan:

1. **Tidak ada koreksi.** Menjiplak dari gambar tidak menolak goresan yang salah, jadi kesalahan tidak terdeteksi.
2. **Aplikasi yang ada terlalu berat.** Aplikasi latihan Hanzi umumnya menyertakan kamus, SRS, kuis, game, akun, dan langganan. Berat dipasang, dan setiap membuka aplikasi kita tertarik ke fitur lain, bukan ke latihan menulis.
3. **Sering butuh internet.** Pemakaian di tempat tanpa sinyal (kelas, perjalanan) jadi tidak bisa.
4. **Tidak relevan dengan target ujian.** Materi yang dijejalkan sering bukan daftar kosakata yang sedang dipelajari.

Kebutuhan yang mengikat: **hanya latihan menulis, aksaranya sesuai HSK 1, bisa dipakai offline, ringan.**

---

## 3. Tujuan & ukuran keberhasilan

| # | Tujuan | Ukuran keberhasilan |
|---|---|---|
| T1 | Melatih pola goresan yang benar | Goresan yang salah secara urutan/bentuk **ditolak** oleh aplikasi, bukan sekadar dinilai |
| T2 | Semua kosakata HSK 1 bisa dilatih | 150 kata HSK 1 tersedia, terbagi dalam 13 pelajaran bertema |
| T3 | Bisa dipakai tanpa internet | Setelah dibuka sekali, aplikasi berjalan tanpa jaringan |
| T4 | Ringan dan siap pakai | Aplikasi terpasang di layar utama HP, terbuka tanpa unduh tambahan |
| T5 | Cepat dipakai | Dari membuka aplikasi sampai goresan pertama bisa ditulis < 5 detik |
| T6 | Tidak ada data pribadi yang dikumpulkan | Tidak ada akun, tidak ada pengiriman data ke mana pun (bisa diperiksa: aplikasi tidak pernah memanggil jaringan) |

---

## 4. Pengguna

**Pengguna utama:** pemelajar Mandarin level pemula yang sedang menyiapkan HSK 1–2 — dalam hal ini pemilik produk sendiri. Karakteristiknya:

- Menulis jauh lebih lemah daripada membaca; butuh koreksi langsung, bukan teori.
- Latihan dilakukan di sela-sela waktu, dengan HP, sering tanpa sinyal.
- Tidak mau mencatat progres atau mengatur jadwal; yang penting langsung bisa menulis.

**Situasi pemakaian:** 3–10 menit, sekali duduk, satu pelajaran, satu tangan memegang HP.

---

## 5. Ruang lingkup

### Termasuk (versi 1)
- Daftar 150 kata HSK 1, dikelompokkan 13 pelajaran bertema (angka, kata ganti, sopan santun, partikel, keluarga, waktu, cuaca & sifat, makan & minum, sekolah, benda, kegiatan, tempat & arah, penunjuk).
- Latihan menulis per aksara: template samar + garis pandu 田字格, koreksi goresan langsung.
- Informasi pinyin + arti bahasa Indonesia untuk setiap kata.
- Penunjuk aksara yang sedang ditulis (untuk kata beraksara banyak, mis. 火车站).
- Tombol "Lihat contoh" (animasi urutan goresan) dan "Hapus" (ulang aksara).
- Navigasi kata sebelumnya/berikutnya.
- Bisa dipasang ke layar utama HP dan dipakai offline (PWA).
- Versi satu berkas HTML untuk dipakai tanpa server sama sekali.

### Tidak termasuk (sengaja, versi 1)
- Skor, nilai akurasi, atau laporan kesalahan.
- Pencatatan progres, streak, atau statistik harian.
- Audio pelafalan.
- Akun, sinkronisasi, dan penyimpanan di server.
- Kamus, contoh kalimat, latihan membaca/mendengar/berbicara.
- Mode gelap, tema, atau pengaturan.
- HSK 2 (150 kata berikutnya) — direncanakan, lihat bagian 12.

Alasan pengecualian ini dibahas satu per satu di bagian 8.

---

## 6. Kebutuhan fungsional

| Kode | Kebutuhan | Prioritas | Status |
|---|---|---|---|
| FR-01 | Menampilkan seluruh 150 kata HSK 1 terkelompok per pelajaran | Wajib | Selesai |
| FR-02 | Mencari & membuka satu kata langsung dari daftar (satu ketukan) | Wajib | Selesai |
| FR-03 | Menampilkan pinyin dan arti Indonesia kata yang dibuka | Wajib | Selesai |
| FR-04 | Menampilkan template samar aksara + garis pandu kotak (田字格) | Wajib | Selesai |
| FR-05 | Menerima goresan pena pengguna lewat sentuhan maupun tetikus | Wajib | Selesai |
| FR-06 | **Menolak** goresan yang salah (bentuk/urutan) dan memberi tanda tanpa memblokir | Wajib | Selesai |
| FR-07 | Menjalankan latihan per aksara: aksara selesai → latihan **berhenti** dan muncul tombol "Aksara berikutnya" (tidak pindah sendiri) | Wajib | Selesai |
| FR-08 | Menandai aksara yang sudah selesai dan aksara yang sedang aktif | Wajib | Selesai |
| FR-09 | Menampilkan penanda jumlah goresan aksara aktif dan mengisinya sesuai kemajuan | Wajib | Selesai |
| FR-10 | Menyatakan kata selesai setelah seluruh aksara ditulis | Wajib | Selesai |
| FR-11 | Animasi contoh urutan goresan atas permintaan ("Lihat contoh") | Sebaiknya | Selesai |
| FR-12 | Mengosongkan kanvas aksara aktif untuk diulang ("Hapus") | Sebaiknya | Selesai |
| FR-13 | Berpindah ke kata berikutnya/sebelumnya tanpa kembali ke daftar | Sebaiknya | Selesai |
| FR-14 | Bekerja penuh tanpa koneksi setelah pembukaan pertama | Wajib | Selesai |
| FR-15 | Bisa dipasang ke layar utama HP (ikon, nama, layar penuh) | Wajib | Selesai |
| FR-16 | Goresan yang **benar tetap terlihat** di kanvas sampai ditekan "Hapus" atau pindah kata | Wajib | Selesai |
| FR-17 | Goresan yang **ditolak tidak meninggalkan tinta** di kanvas | Wajib | Selesai |
| FR-18 | Menyediakan panduan push ke GitHub dan penerbitan (hosting) lewat GitHub Pages | Sebaiknya | Selesai |
| FR-19 | Memutar contoh arah goresan **di dalam kanvas latihan itu sendiri** (bukan kotak terpisah di luar kanvas) | Wajib | Selesai |
| FR-20 | Menampilkan tinta sebagai **bentuk asli goresan aksara** yang **terbuka sedikit demi sedikit mengikuti posisi/arah jari** (bukan coretan jari apa adanya) | Wajib | Selesai |
| FR-21 | Isian berjalan mulus: tidak berkedip dan tidak mundur saat jari bergerak maju-mundur; penilaian goresan tetap dilakukan di akhir goresan | Wajib | Selesai |

## 7. Kebutuhan non-fungsional

| Kode | Kebutuhan | Target | Hasil nyata |
|---|---|---|---|
| NFR-01 | Berat aplikasi | < 1 MB | Data goresan 343 KB + pustaka 37 KB; versi satu berkas **432 KB** |
| NFR-02 | Jumlah permintaan jaringan saat dipakai | 0 setelah pemasangan | Semua berkas lokal; tidak ada CDN/font daring |
| NFR-03 | Waktu tampil daftar | < 1 detik di HP kelas menengah | Data lokal tanpa jaringan, tanpa proses di server |
| NFR-04 | Ketepatan tinta dengan jari | Ukuran kanvas internal pustaka = ukuran tampil (± 1 px) | Terverifikasi: 279 px = 279 px (ada jaring pengaman bila layout bergeser) |
| NFR-05 | Cakupan perangkat | Chrome Android; Safari iOS | Pustaka memakai event sentuh standar (touchstart/move/end) |
| NFR-06 | Privasi | Tidak ada data keluar dari HP | Tidak ada akun, tidak ada pengiriman data ke pihak ketiga; seluruh berkas dilayani dari HP sendiri |
| NFR-07 | Perawatan | Data terpisah dari kode | Kata & goresan di file JSON; menambah kata = menyunting JSON |
| NFR-08 | Ukuran target sentuh | Kanvas 180–340 px, tombol ≥ 44 px tinggi | Kanvas 279–340 px, tombol tidak terpotong (diperiksa otomatis) |

---

## 8. Keputusan yang mengikat (beserta alasannya)

Ini bagian yang paling menentukan bentuk produk. Semua sudah tertanam di aplikasi yang dibangun.

**8.1 Validasi goresan aktif, tapi tanpa angka skor.**
Aplikasi menolak goresan yang salah — itu inti latihan. Tetapi tidak ada perhitungan akurasi, jumlah kesalahan, atau nilai. Alasan: angka mengubah latihan menulis menjadi mengejar nilai, padahal yang dilatih adalah kebiasaan tangan. Umpan baliknya cukup: goresan salah tidak muncul di kanvas dan kotak berkedip merah.

**8.2 Goresan yang benar bertahan; hanya tombol "Hapus" yang menghapus.**
Ini aturan yang diminta pemilik produk setelah memakai aplikasinya ("goresan yang sudah saya tulis langsung otomatis hilang meskipun sudah benar"). Aturannya: satu-satunya cara tinta hilang adalah tombol **Hapus** atau berpindah kata/aksara. Karena itu:

- aplikasi **tidak** memindahkan aksara secara otomatis setelah satu aksara selesai (Pemilik produk memutuskan: pemakai perlu waktu memeriksa tulisannya);
- perubahan ukuran layar kecil (sampai 16 px, mis. scrollbar muncul) **tidak** membangun ulang kanvas;
- kanvas hanya dibangun ulang kalau ukurannya berubah besar (mis. HP diputar), dan ketika itu terjadi aplikasi memberi tahu dengan kalimat yang jelas.

**8.3 Goresan yang ditolak tidak meninggalkan tinta.**
Aturan "goresan salah tidak diterima" harus konsisten dengan yang terlihat: kalau goresan ditolak, gambarnya juga tidak boleh tertinggal. Pustaka Hanzi Writer sendiri menyisakan gambar goresan yang ditolak (diukur: masih terlihat 2 detik kemudian), jadi gambar pustaka dimatikan sama sekali dan isian milik aplikasi yang sedang berjalan dibuang saat goresan ditolak.

**8.4 Template aksara berupa garis tepi, bukan aksara penuh.**
Di awal pembangunan, kanvas menampilkan aksara samar penuh untuk dijiplak. Ternyata pustaka Hanzi Writer memudarkan goresan yang baru ditulis pengguna sambil menampilkan goresan aksara aslinya — dan karena aksara aslinya sudah tampil sejak awal, tulisan yang sudah benar itu seolah hilang. Perbaikannya: template digambar sebagai **garis tepi kosong**, dan tinta yang terlihat digambar oleh **lapisan milik aplikasi sendiri** (bentuk asli goresan, lihat FR-20), sehingga tetap terlihat sampai tombol Hapus ditekan. Ini juga lebih mendidik: pemakai melihat aksaranya terbentuk dari tulisannya sendiri, bukan dari aksara contoh.

**8.5 Berbentuk PWA, bukan aplikasi Android asli (Flutter).**
Alasan utamanya praktis: Android Studio + Flutter SDK memakan 10–12 GB, sedangkan ruang disk laptop yang dipakai tersisa ± 11 GB. PWA juga memberi tiga keuntungan tambahan: bisa dicoba langsung di laptop dan di HP dengan berkas yang sama, bisa dipasang ke layar utama tanpa toko aplikasi, dan bisa dibuka tanpa pemasangan sama sekali (versi satu berkas).

**8.6 Memakai pustaka Hanzi Writer (lisensi MIT).**
Data bentuk dan urutan goresan untuk ± 9.000 aksara adalah hal yang mahal untuk dibuat sendiri dan tidak realistis ditulis manual. Pustaka ini sudah menyediakan: gambar aksara dari data goresan, animasi urutan, dan mode kuis yang memvalidasi goresan — persis kebutuhan FR-04 sampai FR-11. Alternatif "menggambar sendiri di HTML canvas lalu membandingkan gambar" ditolak karena akan menerima goresan yang salah selama gambarnya mirip — justru kelemahan yang mau dihilangkan.

**8.7 Latihan satu aksara besar, bukan satu kanvas untuk seluruh kata.**
Pada awalnya kanvas dibagi rata untuk tiap aksara. Untuk kata 3 aksara di layar HP 360 px, tiap kotak hanya 100 px — terlalu kecil untuk jari dan untuk menilai bentuk goresan. Karena itu satu kanvas besar (279–340 px) dengan penunjuk aksara di atasnya. Ini juga membuat koreksi lebih jelas.

**8.8 Satu file data (343 KB) dimuat sekaligus, bukan per aksara.**
Aplikasi memuat seluruh data goresan sekali di awal. Alternatif "unduh saat dibutuhkan" (cara bawaan pustaka, dari CDN) ditolak karena melanggar syarat offline: latihan aksara baru akan gagal saat tidak ada sinyal.

**8.9 Tanpa pencatatan progres.**
Tidak ada streak maupun statistik. Alasan: menambah penyimpanan, fitur, dan beban kognitif untuk sesuatu yang tidak diminta; pengguna berpindah kata dari daftar sesuai kebutuhan pelajaran di kelas. Bila nanti terbukti dibutuhkan, ini bisa ditambahkan tanpa mengubah struktur data.

**8.10 Batas kesabaran tetap ada: petunjuk setelah 2 kali salah.**
Bila pengguna salah dua kali pada goresan yang sama, aplikasi menampilkan kilasan goresan yang benar. Ini tidak dicatat dan tidak dihitung — hanya bantuan agar tidak macet.

**8.11 Contoh arah goresan diputar di dalam kanvas yang akan dicoret (FR-19).**
Versi sebelumnya menaruh contoh di kotak terpisah di luar kanvas. Pemilik produk memintanya kembali seperti versi pertama: contoh harus tampak **tersimulasi di tempat yang akan dicoret**, supaya arah goresannya langsung terbaca. Karena itu kotak contoh dihapus dan contoh digambar oleh aplikasi sendiri di dalam kanvas (garis tengah goresan, merah pucat, dengan animasi `stroke-dashoffset`). Keuntungan teknisnya sekaligus: contoh tidak lagi memakai `animateStroke` milik pustaka, sehingga penilaian goresan tidak ikut dibatalkan (`cancelQuiz`) — dulu hal ini membuat uji "ganti contoh di tengah latihan" rapuh.

**8.12 Tinta = bentuk asli goresan, dibuka mengikuti jari (FR-20, FR-21).**
Sebelumnya kanvas menampilkan **jalur jari apa adanya** (bawaan pustaka) — terlihat seperti coretan, bukan goresan aksara. Sekarang data `strokes.json` dimanfaatkan sampai ke bentuknya: setiap goresan punya **bentuk asli** (jalur tertutup) dan **garis tengah** (arah goresan). Aplikasi menampilkan bentuk asli itu, dipotong oleh "koridor" — pita selebar ketebalan goresan itu — yang dibangun dari posisi jari di sepanjang garis tengah. Hasilnya: aksara terisi sedikit demi sedikit tepat sejauh jari berjalan, ujung depannya dibulatkan seperti kuas, dan ukuran "sudah ditempuh" hanya boleh bertambah sehingga tampilan tidak berkedip saat jari bergerak maju-mundur. Begitu goresan dinilai benar (di akhir goresan), koridor dilepas dan bentuk goresan itu tampil utuh serta menetap.

---

## 9. Kriteria penerimaan & hasil ujinya

Aplikasi tidak dinilai dari "kodenya jalan", tetapi dari perilaku yang bisa diperiksa. Seluruh pengujian dijalankan pada aplikasi asli dengan menekan kanvas pada koordinat yang diambil dari data goresan — jadi goresan yang dipakai memang goresan asli, bukan simulasi tampilan.

**Hasil: 56 dari 56 pemeriksaan lulus** (keluaran mentah tersimpan di `docs/hasil-uji.txt`).

Ringkasan yang paling penting:

| Yang diperiksa | Hasil |
|---|---|
| 150 kata HSK 1 tampil, 13 pelajaran, 150 tombol | Lulus |
| Data goresan 178 aksara unik dimuat | Lulus |
| Pinyin + arti Indonesia tampil (`wǒmen` / `kami; kita`) | Lulus |
| Aksara 我 dikenali punya 7 goresan | Lulus |
| **Goresan salah ditolak** (0 penanda terisi) + kotak berkedip merah | Lulus |
| **Goresan salah tidak meninggalkan tinta** di kanvas | Lulus |
| **Contoh arah diputar di dalam kanvas** (bukan di kotak terpisah), berjalan, dan menyingkir saat mulai menulis | Lulus |
| **Tinta = bentuk asli goresan** (jalur isian sama persis dengan data) dan tumbuh mengikuti kursor | Lulus |
| **Tidak ada coretan mentah** jalur jari yang terlihat di kanvas | Lulus |
| **Isian tidak mundur** saat jari mundur (tidak berkedip) | Lulus |
| **Ketujuh goresan benar diterima berurutan** (7/7) | Lulus |
| **Goresan benar tetap terlihat**: 2,2 detik setelah ditulis, dan setelah layar berubah ukuran | Lulus |
| **Latihan berhenti** saat aksara selesai + tombol "Aksara berikutnya" muncul (tidak pindah sendiri) | Lulus |
| Tombol "Aksara berikutnya" benar-benar pindah ke 们 dan tinta dihapus | Lulus |
| Kata selesai → pesan "Selesai" dan hanya tombol Daftar yang disediakan | Lulus |
| Tombol Lihat contoh / Hapus / Berikutnya / Sebelumnya / Daftar | Lulus |
| Kotak contoh tidak mengganggu kanvas latihan (tinta latihan utuh) | Lulus |
| Ukuran kanvas internal = ukuran tampil (279 px = 279 px) | Lulus |
| Tinta terlihat pada potret layar: 0 piksel (tanpa goresan) vs 11.818 piksel (aksara lengkap) | Lulus |
| Tidak ada error JavaScript selama pengujian | Lulus |

## 10. Batasan & asumsi

- **Ukuran data** mengikuti pustaka: 178 aksara HSK 1 = 343 KB. Menambah HSK 2 (± 150 kata lagi, ± 250 aksara baru) menambah ± 500 KB — masih jauh di bawah 1 MB.
- **Pinyin dan arti Indonesia disusun manual** untuk aplikasi ini. Daftar kata mengikuti HSK 1 standar (150 kata, dicocokkan satu-satu), tetapi padanan Indonesia belum diperiksa penutur asli atau ahli bahasa. Ini keterbatasan yang disadari, bukan hal yang disembunyikan.
- **Pemasangan PWA** memerlukan alamat http/https. Membuka berkas langsung dari penyimpanan (`file://`) memakai versi satu berkas, dan pada cara ini pemasangan ke layar utama tidak tersedia (offline tetap jalan).
- **Perubahan ukuran layar** yang besar (mis. memutar HP) memuat ulang aksara yang sedang ditulis; goresan yang sudah selesai pada aksara itu perlu diulang. Aplikasi memberi tahu hal ini dengan kalimat yang jelas. Perubahan ukuran kecil (sampai 16 px) tidak memuat ulang apa pun.

---

## 11. Risiko & penanganan

| Risiko | Dampak | Penanganan |
|---|---|---|
| Arti/pinyin manual ada yang kurang tepat | Salah belajar | Perlu ditinjau penutur asli; kesalahan mudah diperbaiki karena semua teks ada di satu berkas JSON |
| Data goresan dari pihak ketiga (Hanzi Writer / Make Me a Hanzi) punya lisensi berbeda dari kodenya | Masalah hukum bila aplikasi disebar komersial | Kode pustaka MIT; data goresan berasal dari Make Me a Hanzi berlisensi Arphic Public License — perlu dicantumkan bila dibagikan publik. Sudah tercantum di footer aplikasi |
| Pustaka berhenti diperbarui | Fitur baru sulit | Data goresan disimpan terpisah di repo ini; pindah pustaka tidak menghapus data |
| PWA "dibersihkan" oleh sistem HP | Aplikasi hilang dari layar utama | Versi satu berkas HTML bisa disimpan sebagai berkas biasa dan tetap dibuka tanpa server |
| Bergantung pada tampilan browser iOS | Perilaku berbeda di iPhone | Belum diuji di iOS — dicatat sebagai hal yang belum diverifikasi |

---

## 12. Rencana lanjutan

**Versi 1.1 — pakai nyata dulu.** Tambahkan HSK 2 (150 kata) memakai jalur data yang sudah ada, lalu **hapus** atau **tambah** fitur berdasarkan apa yang benar-benar mengganggu saat dipakai.

**Versi 1.2 (kandidat, berdasarkan kebutuhan nyata):** daftar kata yang sering salah (butuh penyimpanan ringan), audio pelafalan, penanda kata yang sudah dikuasai.

**Yang tidak akan ditambahkan:** kuis pilihan ganda, kamus, akun, langganan — semuanya bertentangan dengan alasan aplikasi ini dibuat sesempit mungkin.

**Langkah praktis berikutnya:** menerbitkan aplikasi ke alamat publik (GitHub Pages) supaya bisa dibuka & dipasang di HP dari tautan. Berkas dan panduannya sudah siap (`docs/CARA-PUSH-GITHUB.md`, `.github/workflows/halaman.yml`); yang belum bisa dikerjakan dari sini adalah masuk ke akun GitHub dan menekan tombol penerbitan — itu pekerjaan pemilik produk.
