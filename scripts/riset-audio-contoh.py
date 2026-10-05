"""
Memeriksa format berkas audio Commons dan mengukur hasil konversinya.
Alasan: berkas Commons berformat Ogg Vorbis, dan iOS/Safari TIDAK memutar Ogg Vorbis,
sedangkan aplikasi ini juga dipakai di iPhone. Jadi berkasnya harus dikonversi (ffmpeg).

Jalankan: python scripts/riset-audio-contoh.py     (butuh ffmpeg + ffprobe di PATH)
Keluaran: laporan di layar + riset-audio-contoh.json + folder riset-audio-contoh/ (tidak di-commit)
"""
import json, os, subprocess, time, urllib.parse, urllib.request

UA = {'User-Agent': 'TulisHanzi-riset-audio/1.0 (proyek belajar HSK 1; kontak: mutiaharinil@gmail.com)'}
COMMONS = 'https://commons.wikimedia.org/w/api.php'
SAMPEL = ['Zh-wǒmen.ogg', 'Zh-píngguǒ.ogg', 'Zh-xǐ.ogg']


def ambil(params, percobaan=4):
    url = COMMONS + '?' + urllib.parse.urlencode(params)
    for i in range(percobaan):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45))
        except Exception as e:
            if i == percobaan - 1:
                print('   GAGAL:', e)
                return {}
            time.sleep(2)


def unduh(url, jalur):
    # Wikimedia menolak permintaan tanpa User-Agent yang jelas (HTTP 403).
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
        data = r.read()
    open(jalur, 'wb').write(data)
    return len(data)


os.makedirs('riset-audio-contoh', exist_ok=True)
ringkas = []
print('=== Codec asli & hasil konversi ===')
for nama in SAMPEL:
    d = ambil({'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'iiprop': 'url|size',
               'titles': 'File:' + nama}) or {}
    url = None
    for page in d.get('query', {}).get('pages', {}).values():
        if 'imageinfo' in page:
            url = page['imageinfo'][0]['url']
    if not url:
        print(nama, '-> tidak ada')
        continue
    jalur = 'riset-audio-contoh/' + nama
    bit = unduh(url, jalur)
    info = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                           'stream=codec_name,sample_rate,channels:format=duration',
                           '-of', 'default=nw=1', jalur], capture_output=True, text=True).stdout
    baris = {'nama': nama, 'asli': bit, 'codec': ' '.join(info.split())}
    for ext in ('mp3', 'm4a'):
        keluar = 'riset-audio-contoh/%s.%s' % (nama.rsplit('.', 1)[0], ext)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', jalur,
                        '-ac', '1', '-b:a', '64k', keluar], check=False)
        baris[ext] = os.path.getsize(keluar) if os.path.exists(keluar) else 0
    ringkas.append(baris)
    print('%-22s asli %6d bita | %s | mp3 %6d | m4a %6d'
          % (nama, baris['asli'], baris['codec'], baris['mp3'], baris['m4a']))

if ringkas:
    n = len(ringkas)
    rata = {k: sum(b[k] for b in ringkas) / n for k in ('asli', 'mp3', 'm4a')}
    print()
    print('rata-rata per rekaman: asli %d bita | mp3 %d bita | m4a %d bita'
          % (rata['asli'], rata['mp3'], rata['m4a']))
    for k in ('asli', 'mp3', 'm4a'):
        print('perkiraan untuk 150 kata (%s): %.2f MB' % (k, rata[k] * 150 / 1024 / 1024))
json.dump(ringkas, open('riset-audio-contoh.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
