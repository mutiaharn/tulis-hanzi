"""Membuat salinan aplikasi dengan bug lama untuk keperluan pembuktian.

Bug yang direproduksi: penangan event `resize` yang memasang ulang kanvas pada SETIAP
resize, sehingga di HP goresan pengguna terhapus sendiri saat address bar menutup.

Jalankan: python scripts/buat-bukti-bug.py
Lalu buka: http://127.0.0.1:8778/tests/bukti-bug-resize.html
(hasilnya juga dicatat di docs/hasil-uji.txt)

Salinan TIDAK disimpan permanen di repo — dibuat ulang saat dibutuhkan, supaya tidak
ada dua salinan kode yang bisa saling menyimpang.
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
TUJUAN = os.path.join(ROOT, 'tests', 'bukti-old')

BARU = """    window.addEventListener('resize', function () {
      clearTimeout(state.resizeTimer);
      state.resizeTimer = setTimeout(function () {
        if ($('#screen-practice').hidden) return;
        var target = cellSize();
        if (Math.abs(target - state.size) <= 16) return;
        mountChar(target, 'Ukuran layar berubah cukup banyak, jadi kanvas dibuat ulang. Aksara ini perlu ditulis lagi.');
      }, 250);
    });"""

LAMA = """    window.addEventListener('resize', function () {
      clearTimeout(state.resizeTimer);
      state.resizeTimer = setTimeout(function () {
        if (!$('#screen-practice').hidden) { $('#hw').innerHTML = ''; mountChar(); }
      }, 350);
    });"""

# Penyebab UTAMA goresan hilang: dulu kanvas utama memakai showCharacter: true.
# Pustaka Hanzi Writer memudarkan (opacity -> ~0) goresan yang baru saja ditulis pengguna
# sambil menampilkan goresan asli aksara. Karena aksara aslinya sudah tampil sejak awal,
# tulisan yang sudah benar itu tampak hilang sendiri.
KANVAS_BARU = """      showCharacter: false,
      showOutline: true,
      strokeColor: '#1f2937',         // goresan yang sudah benar (mengisi aksara)"""

KANVAS_LAMA = """      showCharacter: true,
      showOutline: true,
      strokeColor: '#ece4d6',"""


def main():
    shutil.rmtree(TUJUAN, ignore_errors=True)
    shutil.copytree(APP, TUJUAN)
    p = os.path.join(TUJUAN, 'js', 'app.js')
    s = open(p, encoding='utf-8').read()
    for nama, baru, lama in [('penangan resize', BARU, LAMA), ('pengaturan kanvas', KANVAS_BARU, KANVAS_LAMA)]:
        if baru not in s:
            raise SystemExit('%s versi sekarang tidak ditemukan di app/js/app.js — '
                             'perbarui skrip ini lalu jalankan lagi.' % nama)
        s = s.replace(baru, lama)
    open(p, 'w', encoding='utf-8').write(s)
    print('Salinan "versi lama" siap di tests/bukti-old/ (penangan resize lama + kanvas lama dipasang kembali).')
    print('Buka http://127.0.0.1:8778/tests/bukti-bug-resize.html untuk membandingkan.')


if __name__ == '__main__':
    main()
