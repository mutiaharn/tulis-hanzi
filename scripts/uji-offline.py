"""Uji pemakaian offline yang benar-benar membuktikan service worker bekerja.

Masalah pada cara uji sebelumnya: dengan profil Chrome biasa, permintaan halaman masih bisa
dilayani oleh CACHE HTTP biasa milik Chrome, sehingga "aplikasi tetap terbuka tanpa server"
belum tentu bukti service worker. Uji itu sudah diperketat dengan --disk-cache-size=1 (cache
HTTP dimatikan).

Masalah kedua yang ditemukan kemudian: pemasangan service worker dikerjakan oleh PROSES
BROWSER, bukan oleh halaman, jadi tidak ikut dipercepat --virtual-time-budget. Chrome
(headless) sering keluar sebelum simpanan selesai ditulis, sehingga hasil uji offline
bergantung keberuntungan (pernah lulus, pernah kosong -- padahal aplikasinya tidak berubah).
Karena itu uji ini sekarang:

  1. memakai server kecil sendiri yang punya alamat lambat (/lambat?s=2.5) — menunggu 2,5
     detik sebelum menjawab. Selama permintaan itu belum selesai, jam virtual Chrome dalam
     keadaan menunggu, sehingga browser TETAP HIDUP dan pemasangan service worker
     mendapat waktu nyata yang cukup;
  2. membuka aplikasi di dalam bingkai (iframe) pada halaman pemantau, lalu memantau
     putaran demi putaran: jumlah pendaftaran service worker, state-nya, dan isi simpanannya;
  3. memakai alamat /lambat yang selalu berbeda tiap putaran, agar tidak dilayani dari
     simpanan service worker itu sendiri;
  4. setelah itu memeriksa simpanan service worker DI DISK, lalu mematikan server dan
     membuka aplikasi lagi TANPA server dan TANPA cache HTTP.

Jalankan: python scripts/uji-offline.py
Kesimpulan: OFFLINE TERBUKTI bila tanpa server pun aplikasi tetap memuat 150 kata.

Berkas pemantau ditulis sementara ke app/_uji-setup-sw.html dan dihapus lagi di akhir.
"""
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(ROOT, 'app')
PORT = 8777
APP = 'http://127.0.0.1:%d/' % PORT
PROFIL = os.path.join(os.environ.get('TEMP', r'C:\Windows\Temp'), 'chrome-uji-offline')
NAMA_PANTAU = '_uji-setup-sw.html'
PANTAU = os.path.join(APP_DIR, NAMA_PANTAU)
CHROME = [r'C:\Program Files\Google\Chrome\Application\chrome.exe',
          r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
          '/usr/bin/google-chrome', '/usr/bin/chromium']

SERVER = r'''
import functools, http.server, socketserver, sys, time
akar = sys.argv[1]
port = int(sys.argv[2])

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/lambat'):
            detik = 2.5
            try:
                for bagian in self.path.split('?', 1)[1].split('&'):
                    if bagian.startswith('s='):
                        detik = float(bagian[2:])
            except Exception:
                pass
            time.sleep(detik)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(b'lambat')
            return
        return super().do_GET()

    def log_message(self, *a):
        pass

class S(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

with S(('127.0.0.1', port), functools.partial(H, directory=akar)) as srv:
    srv.serve_forever()
'''

PANTAU_HTML = r'''<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8"><title>pantau service worker</title></head>
<body>
<iframe id="app" src="index.html" style="width:380px;height:640px;border:1px solid #ccc"></iframe>
<pre id="out">jalan…</pre>
<script>
/* Halaman pemantau (sementara, dibuat oleh scripts/uji-offline.py).
   Aplikasi dibuka di dalam iframe — jadi yang memasang service worker adalah APLIKASI
   SUNGGUHAN, bukan halaman ini. Tugas halaman ini hanya memberi waktu nyata kepada
   proses browser (lewat permintaan ke /lambat yang sengaja lambat, alamatnya selalu
   berbeda tiap putaran) lalu melaporkan keadaan service worker. */
const out = document.getElementById('out');
const log = [];
const tulis = s => { log.push(s); out.textContent = log.join('\n'); };
let aktifBeruntun = 0;
(async () => {
  try {
    tulis('memulai: ' + location.href);
    for (let r = 1; r <= 10; r++) {
      try { await fetch('/lambat?s=2.5&r=' + r, { cache: 'no-store' }); } catch (e) { tulis('lambat gagal: ' + e.message); }
      const regs = await navigator.serviceWorker.getRegistrations();
      const kunci = await caches.keys();
      let berkas = 0;
      const rincian = [];
      for (const k of kunci) {
        const isi = await (await caches.open(k)).keys();
        berkas += isi.length;
        rincian.push(k + '=' + isi.length);
      }
      let state = 'tidak ada';
      if (regs.length) {
        const r0 = regs[0];
        state = r0.active ? r0.active.state : (r0.installing ? 'installing' : (r0.waiting ? 'waiting' : '-'));
      }
      tulis('putaran ' + r + ': pendaftaran=' + regs.length + ' state=' + state +
            ' cache=' + kunci.length + ' berkas=' + berkas + (rincian.length ? ' [' + rincian.join(', ') + ']' : ''));
      if (regs.length && regs[0].active && regs[0].active.state === 'activated' && berkas > 0) {
        aktifBeruntun++;
        if (aktifBeruntun >= 2) { tulis('HASIL: service worker AKTIF dan simpanannya TERISI'); break; }
      } else {
        aktifBeruntun = 0;
      }
    }
    try {
      const d = document.getElementById('app').contentDocument;
      tulis('kata terbaca di aplikasi: ' + d.querySelectorAll('#lesson-list .chip').length);
    } catch (e) {
      tulis('tidak bisa membaca isi bingkai: ' + e.message);
    }
  } catch (e) {
    tulis('GAGAL: ' + (e && e.message ? e.message : e));
  }
  document.title = 'SIAP';
})();
</script>
</body></html>
'''


def chrome_bin():
    for c in CHROME:
        if os.path.exists(c):
            return c
    sys.exit('Chrome tidak ditemukan.')


def buka(url, anggaran=90000):
    cmd = [chrome_bin(), '--headless=new', '--disable-gpu', '--no-first-run',
           '--disk-cache-size=1',          # matikan cache HTTP biasa
           '--user-data-dir=' + PROFIL, '--window-size=400,940',
           '--virtual-time-budget=%d' % anggaran, '--dump-dom', url]
    return subprocess.run(cmd, capture_output=True, timeout=300).stdout.decode('utf-8', 'replace')


def jumlah_kata(html):
    return len(re.findall(r'class="chip"', html))


def pid_pendengar(port):
    out = subprocess.run(['netstat', '-ano'], capture_output=True).stdout.decode('utf-8', 'replace')
    for b in out.splitlines():
        if (':%d ' % port) in b and 'LISTEN' in b.upper():
            return b.split()[-1]
    return None


def matikan_pendengar(port):
    pid = pid_pendengar(port)
    if pid:
        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
        time.sleep(1)
    return pid


def isi_simpanan_sw():
    dasar = os.path.join(PROFIL, 'Default', 'Service Worker', 'CacheStorage')
    hasil = []
    for akar, _, berkas in os.walk(dasar):
        for n in berkas:
            p = os.path.join(akar, n)
            t = os.path.getsize(p)
            if t > 20000:
                hasil.append((t, os.path.relpath(p, dasar)))
    return sorted(hasil, reverse=True)


def main():
    # Port 8777 dipakai server kecil milik uji ini, jadi server yang sedang jalan
    # (kalau ada) dihentikan dulu — dan dinyalakan lagi di akhir.
    pid_lama = matikan_pendengar(PORT)
    if pid_lama:
        print('0) server yang sedang jalan di port %d dihentikan dulu (PID %s)' % (PORT, pid_lama))
    shutil.rmtree(PROFIL, ignore_errors=True)
    with open(PANTAU, 'w', encoding='utf-8') as f:
        f.write(PANTAU_HTML)
    srv = subprocess.Popen([sys.executable, '-c', SERVER, APP_DIR, str(PORT)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.5)
        print('1) server kecil + alamat lambat jalan di port %d' % PORT)
        h = buka(APP + NAMA_PANTAU)
        m = re.search(r'<pre id="out">(.*?)</pre>', h, re.S)
        laporan = (m.group(1) if m else 'TIDAK ADA LAPORAN')
        laporan = laporan.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'")
        for baris in laporan.splitlines():
            print('   ' + baris.strip())

        isi = isi_simpanan_sw()
        print('2) isi simpanan service worker di disk (>20 KB): %d berkas' % len(isi))
        for t, p in isi[:8]:
            print('   %9d B  %s' % (t, p[:66]))
        if not isi:
            print('   CATATAN: simpanan masih kosong — service worker belum selesai menyimpan.')

        print('3) server dimatikan')
        srv.terminate()
        try:
            srv.wait(timeout=10)
        except Exception:
            srv.kill()
        matikan_pendengar(PORT)
        time.sleep(1)
        print('   port %d kosong? %s' % (PORT, pid_pendengar(PORT) is None))

        print('4) buka aplikasi lagi TANPA server dan TANPA cache HTTP')
        n2 = jumlah_kata(buka(APP))
        print('   kata terbaca:', n2)

        print('5) minta alamat yang tidak ada, tanpa server')
        h3 = buka(APP + 'alamat-yang-tidak-ada')
        halaman_app = 'Tulis Hanzi' in h3 and 'id="lesson-list"' in h3
        print('   halaman aplikasi dikembalikan:', halaman_app, '| halaman error Chrome:', 'ERR_' in h3)
    finally:
        if srv.poll() is None:
            srv.terminate()
        if os.path.exists(PANTAU):
            os.remove(PANTAU)              # jangan tinggalkan berkas uji di folder aplikasi

    # Kembalikan keadaan seperti semula: server aplikasi biasa dinyalakan lagi di port 8777.
    subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT),
                      '--directory', APP_DIR, '--bind', '127.0.0.1'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    print('6) server aplikasi biasa dinyalakan lagi -> port %d hidup: %s'
          % (PORT, pid_pendengar(PORT) is not None))

    print()
    if n2 >= 150:
        print('KESIMPULAN: OFFLINE TERBUKTI. Cache HTTP dimatikan, jadi hanya service worker')
        print('            yang mungkin melayani aplikasi tanpa server.')
        return 0
    print('KESIMPULAN: BELUM TERBUKTI (aplikasi tidak terbuka tanpa server).')
    return 1


if __name__ == '__main__':
    sys.exit(main())
