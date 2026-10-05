"""Pembaca PNG sederhana (8-bit RGB/RGBA, tanpa antar-jalin) memakai zlib bawaan Python.

Dipakai oleh scripts/hitung-tinta.py dan scripts/banding-gambar.py.
"""
import struct
import zlib


def baca_png(path):
    data = open(path, 'rb').read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise SystemExit('Bukan berkas PNG: ' + path)
    pos, idat, ihdr = 8, [], None
    while pos < len(data):
        panjang = struct.unpack('>I', data[pos:pos + 4])[0]
        jenis = data[pos + 4:pos + 8]
        isi = data[pos + 8:pos + 8 + panjang]
        if jenis == b'IHDR':
            ihdr = struct.unpack('>IIBBBBB', isi)
        elif jenis == b'IDAT':
            idat.append(isi)
        elif jenis == b'IEND':
            break
        pos += 12 + panjang
    lebar, tinggi, kedalaman, warna, _, _, antar = ihdr
    if kedalaman != 8 or warna not in (2, 6) or antar != 0:
        raise SystemExit('Hanya mendukung PNG 8-bit RGB/RGBA tanpa antar-jalin '
                         '(ditemukan kedalaman=%d warna=%d antarjalin=%d)' % (kedalaman, warna, antar))
    kanal = 3 if warna == 2 else 4
    mentah = zlib.decompress(b''.join(idat))
    langkah = lebar * kanal
    keluar = bytearray(langkah * tinggi)
    sebelum = bytearray(langkah)
    p = 0
    for y in range(tinggi):
        tapis = mentah[p]
        p += 1
        baris = bytearray(mentah[p:p + langkah])
        p += langkah
        if tapis == 1:
            for i in range(kanal, langkah):
                baris[i] = (baris[i] + baris[i - kanal]) & 255
        elif tapis == 2:
            for i in range(langkah):
                baris[i] = (baris[i] + sebelum[i]) & 255
        elif tapis == 3:
            for i in range(langkah):
                a = baris[i - kanal] if i >= kanal else 0
                baris[i] = (baris[i] + ((a + sebelum[i]) >> 1)) & 255
        elif tapis == 4:
            for i in range(langkah):
                a = baris[i - kanal] if i >= kanal else 0
                b = sebelum[i]
                c = sebelum[i - kanal] if i >= kanal else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                perkiraan = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                baris[i] = (baris[i] + perkiraan) & 255
        keluar[y * langkah:(y + 1) * langkah] = baris
        sebelum = baris
    return lebar, tinggi, kanal, bytes(keluar)


def cahaya(piksel, i):
    r, g, b = piksel[i], piksel[i + 1], piksel[i + 2]
    return (r * 299 + g * 587 + b * 114) // 1000
