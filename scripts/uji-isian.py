"""Mengukur isian tinta dan contoh arah goresan lewat potret layar.

Menjawab pertanyaan yang tidak bisa dijawab hanya dengan membaca kode:
  1. apakah isian bertambah banyak saat goresan bertambah? (kosong < tengah < diterima)
  2. apakah "pita" pengungkap isian cukup lebar, sehingga bentuk aksara tidak terpotong di
     pinggirnya? (penuh vs diterima: jumlah piksel harus hampir sama)
  3. apakah isian tumbuh bertahap, bukan langsung penuh? (tengah harus jelas < penuh)
  4. apakah contoh arah goresan digambar DI DALAM kanvas — bukan di kotak terpisah?
     (piksel warna contoh, dan sebarannya harus berada di dalam kotak kanvas)
  5. apakah contoh itu menyingkir begitu pengguna mulai menulis? (tengah/tiga: tidak ada piksel contoh)

Pemakaian (server aplikasi 8777 dan server akar 8778 harus hidup):
    python scripts/uji-isian.py
Potret disimpan di docs/isian-<mode>.png
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = [r'C:\Program Files\Google\Chrome\Application\chrome.exe',
          r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
          '/usr/bin/google-chrome', '/usr/bin/chromium']
TEMP = os.environ.get('TEMP', r'C:\Windows\Temp')
HALAMAN = 'http://127.0.0.1:8778/tests/alat-ukur/foto-isian.html'
MODES = ['kosong', 'contoh', 'tengah', 'penuh', 'diterima', 'tiga']


def chrome():
    for c in CHROME:
        if os.path.exists(c):
            return c
    sys.exit('Chrome tidak ditemukan.')


def jalankan(url, ekstra, anggaran=30000):
    profil = os.path.join(TEMP, 'chrome-isian-kerja')
    shutil.rmtree(profil, ignore_errors=True)
    cmd = [chrome(), '--headless=new', '--disable-gpu', '--no-first-run',
           '--user-data-dir=' + profil, '--window-size=420,820',
           '--virtual-time-budget=%d' % anggaran] + ekstra + [url]
    return subprocess.run(cmd, capture_output=True, timeout=300)


def potret(mode):
    keluaran = os.path.join(ROOT, 'docs', 'isian-%s.png' % mode)
    jalankan(HALAMAN + '?mode=' + mode, ['--screenshot=' + keluaran])
    return keluaran if os.path.exists(keluaran) else None


def kotak_kanvas():
    """Kotak kanvas di dalam potret (halaman potret menaruh aplikasi di 0,0)."""
    hasil = jalankan(HALAMAN + '?mode=kosong', ['--dump-dom'], 12000)
    m = re.search(r'<pre id="info"[^>]*>(.*?)</pre>',
                  hasil.stdout.decode('utf-8', 'replace'), re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def hitung(path, kanvas=None):
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    from png import baca_png, cahaya
    lebar, tinggi, kanal, piksel = baca_png(path)
    gelap = sedang = contoh = 0
    cx0, cy0, cx1, cy1 = lebar, tinggi, -1, -1
    # piksel contoh hanya dihitung DI DALAM kanvas (disisakan 8 px dari tepi), supaya cincin
    # merah penanda salah dan warna aksen antarmuka aplikasi tidak ikut terhitung
    if kanvas:
        kx0, ky0 = int(kanvas['x']) + 8, int(kanvas['y']) + 8
        kx1, ky1 = int(kanvas['x'] + kanvas['w']) - 8, int(kanvas['y'] + kanvas['h']) - 8
    else:
        kx0, ky0, kx1, ky1 = 0, 0, lebar, tinggi
    for y in range(tinggi):
        dasar = y * lebar * kanal
        for x in range(lebar):
            i = dasar + x * kanal
            c = cahaya(piksel, i)
            if c < 100:
                gelap += 1
            elif c < 200:
                sedang += 1
            if kx0 <= x < kx1 and ky0 <= y < ky1:
                r, g, b = piksel[i], piksel[i + 1], piksel[i + 2]
                # warna contoh: merah aksen #b91c1c pada kepekatan 50% di atas kertas terang
                if r > 190 and 110 < g < 180 and 110 < b < 180:
                    contoh += 1
                    cx0, cy0 = min(cx0, x), min(cy0, y)
                    cx1, cy1 = max(cx1, x), max(cy1, y)
    kotak = None if cx1 < 0 else (cx0, cy0, cx1, cy1)
    return {'gelap': gelap, 'sedang': sedang, 'contoh': contoh, 'kotak_contoh': kotak}


def main():
    kanvas = kotak_kanvas()
    print('kotak kanvas di potret (x, y, lebar, tinggi, panjang jalur contoh):', kanvas)
    hasil = {}
    for mode in MODES:
        kel = potret(mode)
        if not kel:
            print('GAGAL memotret mode', mode)
            continue
        hasil[mode] = hitung(kel, kanvas)
        h = hasil[mode]
        print('%-9s gelap=%7d  sedang=%7d  piksel contoh=%6d  sebaran=%s'
              % (mode, h['gelap'], h['sedang'], h['contoh'], h['kotak_contoh']))
    print()

    if len(hasil) < len(MODES):
        print('PERIKSA: ada mode yang gagal dipotret')
        return 1

    def tinta(mode):
        return hasil[mode]['gelap']

    kosong, tengah, penuh = tinta('kosong'), tinta('tengah'), tinta('penuh')
    diterima, tiga = tinta('diterima'), tinta('tiga')
    tumbuh = tengah - kosong
    total = diterima - kosong

    print('1. isian bertambah saat ditulis : kosong=%d < tengah=%d < diterima=%d -> %s'
          % (kosong, tengah, diterima, 'BENAR' if kosong < tengah < diterima else 'PERIKSA'))
    print('   isian pada 55%% goresan       : %d dari %d piksel (%.0f%%) -> %s'
          % (tumbuh, total, 100.0 * tumbuh / max(1, total),
             'BENAR (bertahap, tidak langsung penuh)' if tumbuh < 0.9 * total else 'PERIKSA'))
    selisih = abs(penuh - diterima)
    print('2. pita tidak memotong aksara   : penuh=%d vs diterima=%d (selisih %d = %.1f%% dari tinta) -> %s'
          % (penuh, diterima, selisih, 100.0 * selisih / max(1, total),
             'AMAN' if selisih <= 0.05 * max(1, total) else 'PERIKSA'))
    print('3. tiga goresan menambah tinta  : %d > %d -> %s'
          % (tiga, diterima, 'BENAR' if tiga > diterima else 'PERIKSA'))

    contoh_kosong = hasil['kosong']['contoh']
    kotak = hasil['kosong']['kotak_contoh']
    di_dalam = False
    if kotak and kanvas:
        di_dalam = (kotak[0] >= kanvas['x'] and kotak[1] >= kanvas['y'] and
                    kotak[2] <= kanvas['x'] + kanvas['w'] and kotak[3] <= kanvas['y'] + kanvas['h'])
    print('4. contoh digambar DI DALAM kanvas: %d piksel contoh, sebaran %s, jalur %d huruf -> %s'
          % (contoh_kosong, kotak, (kanvas or {}).get('contoh', 0),
             'BENAR' if (contoh_kosong > 300 and di_dalam) else 'PERIKSA'))
    ct, c3 = hasil['tengah']['contoh'], hasil['tiga']['contoh']
    print('5. contoh menyingkir saat menulis: tengah=%d, tiga=%d -> %s'
          % (ct, c3, 'BENAR' if ct == 0 and c3 == 0 else 'PERIKSA'))

    lulus = (kosong < tengah < diterima and tumbuh < 0.9 * total and
             selisih <= 0.05 * max(1, total) and tiga > diterima and
             contoh_kosong > 300 and di_dalam and ct == 0 and c3 == 0)
    print()
    print('RINGKASAN: %s' % ('SEMUA PEMERIKSAAN ISIAN DAN CONTOH LULUS' if lulus
                             else 'ADA YANG PERLU DIPERIKSA'))
    return 0 if lulus else 1


if __name__ == '__main__':
    sys.exit(main())
