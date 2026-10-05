"""Menghitung piksel gelap pada potret layar PNG — untuk membuktikan tinta benar-benar terlihat.

Pemakaian:
    python scripts/hitung-tinta.py <berkas.png> [x0 y0 x1 y1]
Tanpa koordinat, seluruh gambar dihitung.

Keluaran: jumlah piksel gelap (tinta), sedang (garis bantu), terang (kertas) + persentase.
"""
import sys

from png import baca_png, cahaya


def hitung(lebar, tinggi, kanal, piksel, kotak):
    x0, y0, x1, y1 = kotak
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(lebar, x1), min(tinggi, y1)
    gelap = sedang = terang = 0
    for y in range(y0, y1):
        dasar = y * lebar * kanal
        for x in range(x0, x1):
            i = dasar + x * kanal
            c = cahaya(piksel, i)
            if c < 100:
                gelap += 1
            elif c < 200:
                sedang += 1
            else:
                terang += 1
    return gelap, sedang, terang


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = sys.argv[1]
    lebar, tinggi, kanal, piksel = baca_png(path)
    kotak = tuple(int(v) for v in sys.argv[2:6]) if len(sys.argv) >= 6 else (0, 0, lebar, tinggi)
    gelap, sedang, terang = hitung(lebar, tinggi, kanal, piksel, kotak)
    jumlah = gelap + sedang + terang
    print('%s  ukuran=%dx%d  kotak=%s' % (path, lebar, tinggi, kotak))
    print('  piksel dihitung : %d' % jumlah)
    print('  GELAP (tinta)   : %d  (%.2f%%)' % (gelap, 100.0 * gelap / jumlah))
    print('  sedang (garis)  : %d  (%.2f%%)' % (sedang, 100.0 * sedang / jumlah))
    print('  terang (kertas) : %d  (%.2f%%)' % (terang, 100.0 * terang / jumlah))


if __name__ == '__main__':
    main()
