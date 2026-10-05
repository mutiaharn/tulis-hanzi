"""Membandingkan dua potret layar PNG: berapa piksel yang berbeda dan di mana letaknya.

Dipakai untuk membuktikan "tinta tetap terlihat": dua versi aplikasi diberi perlakuan yang
sama, lalu potretnya dibandingkan piksel demi piksel. Wilayah yang berbeda = perbedaannya.

Pemakaian:
    python scripts/banding-gambar.py <a.png> <b.png> [ambang]
    (ambang bawaan 24; piksel dianggap berbeda kalau selisih salah satu warnanya > ambang)
"""
import sys

from png import baca_png, cahaya


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    a, b = sys.argv[1], sys.argv[2]
    ambang = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    wa, ha, ka, pa = baca_png(a)
    wb, hb, kb, pb = baca_png(b)
    if (wa, ha) != (wb, hb):
        raise SystemExit('Ukuran berbeda: %dx%d vs %dx%d' % (wa, ha, wb, hb))
    beda = 0
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    gelapA = gelapB = 0
    for y in range(ha):
        dasarA = y * wa * ka
        dasarB = y * wb * kb
        for x in range(wa):
            ia = dasarA + x * ka
            ib = dasarB + x * kb
            if (abs(pa[ia] - pb[ib]) > ambang or abs(pa[ia + 1] - pb[ib + 1]) > ambang
                    or abs(pa[ia + 2] - pb[ib + 2]) > ambang):
                beda += 1
                x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
                if cahaya(pa, ia) < 100:
                    gelapA += 1
                if cahaya(pb, ib) < 100:
                    gelapB += 1
    print('A = %s\nB = %s' % (a, b))
    print('  ukuran sama        : %dx%d' % (wa, ha))
    print('  piksel berbeda     : %d  (%.2f%% dari %d piksel)' % (beda, 100.0 * beda / (wa * ha), wa * ha))
    if beda:
        print('  wilayah berbeda    : x %d..%d , y %d..%d' % (x0, x1, y0, y1))
        print('  di wilayah itu, piksel gelap: A=%d  B=%d' % (gelapA, gelapB))
    else:
        print('  kedua potret identik pada ambang %d' % ambang)


if __name__ == '__main__':
    main()
