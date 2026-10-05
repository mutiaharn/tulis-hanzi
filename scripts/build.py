"""Bangun tiga hal dari satu sumber:
1. ikon PNG (192 & 512) bermotif 田字格,
2. versi cache service worker (app/sw.js) — dihitung dari isi berkas, supaya HP yang sudah
   pernah membuka aplikasi selalu mengambil versi terbaru setelah aplikasi diperbarui,
3. dist/tulis-hanzi-satu-file.html — seluruh aplikasi + data digabung jadi SATU berkas,
   supaya bisa dibuka langsung dari HP tanpa server (klik dua kali / kirim ke HP).
Jalankan: python scripts/build.py
"""
import hashlib, json, os, re, struct, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
DIST = os.path.join(ROOT, 'dist')

# berkas yang isinya menentukan versi cache (kalau salah satu berubah, cache ikut berubah)
BERKAS_CACHE = ['index.html', 'css/style.css', 'js/app.js', 'data/hsk1.json',
                'data/strokes.json', 'vendor/hanzi-writer.min.js']


def versi_cache():
    """Sidik jari isi aplikasi -> dipakai sebagai nama cache service worker."""
    h = hashlib.sha256()
    for nama in BERKAS_CACHE:
        p = os.path.join(APP, *nama.split('/'))
        h.update(nama.encode('utf-8'))
        with open(p, 'rb') as f:
            h.update(f.read())
    return h.hexdigest()[:10]


def perbarui_cache():
    p = os.path.join(APP, 'sw.js')
    s = open(p, encoding='utf-8').read()
    baru = "var CACHE = 'tulis-hanzi-%s';" % versi_cache()
    s2, n = re.subn(r"var CACHE = 'tulis-hanzi-[^']*';", baru, s)
    if n != 1:
        raise SystemExit('Baris "var CACHE = ..." tidak ditemukan sekali di app/sw.js (ditemukan %d).' % n)
    if s2 != s:
        open(p, 'w', encoding='utf-8').write(s2)
        print('cache :', baru)
    else:
        print('cache :', baru, '(tidak berubah)')


# ---------------------------------------------------------------- ikon PNG
def write_png(path, size, pixel):
    raw = bytearray()
    for y in range(size):
        raw.append(0)                                   # filter 0
        for x in range(size):
            r, g, b = pixel(x, y)
            raw += bytes((r & 255, g & 255, b & 255))
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    open(path, 'wb').write(png)

def make_icon(path, size, ss=3):
    """Kertas + garis merah 田字格 tipis + satu goresan tinta (撇).
    Digambar 3x lalu diperkecil, jadi tepinya halus."""
    N = size * ss
    pad = N * 0.15
    line = max(ss * 1.2, N * 0.022)
    x0, x1 = pad, N - 1 - pad
    paper, red, ink = (253, 251, 247), (185, 28, 28), (31, 41, 55)
    mid = (x0 + x1) / 2
    a = (N * 0.66, N * 0.30)      # pangkal goresan
    b = (N * 0.34, N * 0.70)      # ujung goresan

    def goresan(x, y):
        ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        t = ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)
        t = 0 if t < 0 else (1 if t > 1 else t)
        d = ((x - (ax + t * dx)) ** 2 + (y - (ay + t * dy)) ** 2) ** 0.5
        return d <= N * (0.062 - 0.030 * t) / 2

    def grid(x, y):
        if x0 - line <= y <= x1 + line and (abs(x - x0) < line or abs(x - x1) < line):
            return True
        if x0 - line <= x <= x1 + line and (abs(y - x0) < line or abs(y - x1) < line):
            return True
        if x0 <= x <= x1 and abs(x - mid) < line / 2:
            return True
        if x0 <= y <= x1 and abs(y - mid) < line / 2:
            return True
        return False

    def pixel(x, y):
        r = g = b_ = 0
        for dy in range(ss):
            for dx in range(ss):
                X, Y = x * ss + dx, y * ss + dy
                c = ink if goresan(X, Y) else (red if grid(X, Y) else paper)
                r += c[0]; g += c[1]; b_ += c[2]
        n = ss * ss
        return (r // n, g // n, b_ // n)

    write_png(path, size, pixel)
    print('ikon  :', os.path.relpath(path, ROOT), size, 'x', size)

# ---------------------------------------------------------------- satu berkas
def build_single_file():
    html = open(os.path.join(APP, 'index.html'), encoding='utf-8').read()
    css = open(os.path.join(APP, 'css', 'style.css'), encoding='utf-8').read()
    lib = open(os.path.join(APP, 'vendor', 'hanzi-writer.min.js'), encoding='utf-8').read()
    app = open(os.path.join(APP, 'js', 'app.js'), encoding='utf-8').read()
    hsk1 = open(os.path.join(APP, 'data', 'hsk1.json'), encoding='utf-8').read()
    strokes = open(os.path.join(APP, 'data', 'strokes.json'), encoding='utf-8').read()

    html = html.replace('<link rel="manifest" href="manifest.webmanifest">\n', '')
    html = html.replace('<link rel="icon" href="icons/icon-192.png">\n', '')
    html = html.replace('<link rel="apple-touch-icon" href="icons/icon-192.png">\n', '')
    html = html.replace('<link rel="stylesheet" href="css/style.css">',
                        '<style>\n' + css + '\n</style>')
    html = html.replace('<script src="vendor/hanzi-writer.min.js"></script>',
                        '<script>\n' + lib + '\n</script>')
    html = html.replace('<script src="js/app.js"></script>',
                        '<script>window.__BUNDLE__={hsk1:' + hsk1 + ',strokes:' + strokes + '};</script>\n'
                        '<script>\n' + app + '\n</script>')
    assert '__BUNDLE__' in html, 'penyisipan data gagal'
    assert 'src="vendor' not in html and 'href="css' not in html, 'masih ada rujukan berkas luar'
    out = os.path.join(DIST, 'tulis-hanzi-satu-file.html')
    open(out, 'w', encoding='utf-8').write(html)
    print('satu berkas:', os.path.relpath(out, ROOT), round(os.path.getsize(out) / 1024), 'KB')

if __name__ == '__main__':
    os.makedirs(DIST, exist_ok=True)
    make_icon(os.path.join(APP, 'icons', 'icon-192.png'), 192)
    make_icon(os.path.join(APP, 'icons', 'icon-512.png'), 512)
    perbarui_cache()
    build_single_file()
