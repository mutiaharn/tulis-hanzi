"""
Riset audio pengucapan HSK 1 — satu skrip untuk semua pengukuran.
Hasilnya dipakai untuk docs/RISET-AUDIO.md. Sumber data: API Wikimedia Commons dan Wiktionary.

Jalankan: python scripts/riset-audio.py
Keluaran: laporan di layar + riset-audio-hasil.json (tidak di-commit, lihat .gitignore)

Yang diukur:
  1. Rekaman pengucapan PER KATA  (pola nama berkas "Zh-<pinyin>.ogg")
  2. Variasi penulisan nama berkas untuk kata yang belum ditemukan
  3. Rekaman PER AKSARA (pola "Zh-<aksara>.ogg" dan nama berkas yang dipakai halaman Wiktionary)
  4. Penutur & lisensi tiap berkas (CC BY mewajibkan nama penutur dicantumkan)
  5. Bisakah kata yang belum punya rekaman ditambal dari rekaman SUKU KATA?
Untuk format berkas & konversi (Ogg -> MP3/M4A) lihat scripts/riset-audio-contoh.py
"""
import json, re, time, urllib.parse, urllib.request
from collections import Counter

UA = {'User-Agent': 'TulisHanzi-riset-audio/1.0 (proyek belajar HSK 1; kontak: mutiaharinil@gmail.com)'}
COMMONS = 'https://commons.wikimedia.org/w/api.php'
WIKTIONARY = 'https://en.wiktionary.org/w/api.php'
BERKAS_AUDIO = re.compile(r'[A-Za-z0-9\u00c0-\u024f\u4e00-\u9fff][\w\u00c0-\u024f\u4e00-\u9fff\'\-]*\.(?:ogg|oga|wav|mp3)', re.I)

# Suku kata yang dibutuhkan untuk menambal kata yang belum punya rekaman.
# Disusun manual dari pinyin kata-katanya (data aplikasi hanya menyimpan pinyin per kata).
SUKU_TAMBALAN = {
    '谁': ['shéi', 'shuí'], '不客气': ['bú', 'bù', 'kè', 'qi'], '小姐': ['xiǎo', 'jiě'],
    '饭馆': ['fàn', 'guǎn'], '说话': ['shuō', 'huà'], '电脑': ['diàn', 'nǎo'],
    '猫': ['māo'], '狗': ['gǒu'], '打电话': ['dǎ', 'diàn', 'huà'], '前面': ['qián', 'miàn'],
    '后面': ['hòu', 'miàn'], '火车站': ['huǒ', 'chē', 'zhàn'], '北京': ['běi', 'jīng'],
    '中国': ['zhōng', 'guó'], '出租车': ['chū', 'zū', 'chē'],
}
# Variasi penulisan nama berkas yang di Commons: spasi dan apostrof dihilangkan.
VARIAN = {'méi guānxi': 'méiguānxi', "nǚ'ér": 'nǚér', 'Hànyǔ': 'hànyǔ', 'xià yǔ': 'xiàyǔ'}


def ambil(base, params, percobaan=4):
    url = base + '?' + urllib.parse.urlencode(params)
    for i in range(percobaan):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45))
        except Exception as e:
            if i == percobaan - 1:
                print('   GAGAL:', e)
                return {}
            time.sleep(2)


def inti(judul):
    """'File:Zh-wǒmen.ogg' -> 'wǒmen' (buang awalan File:, awalan Zh-, dan ekstensi)."""
    j = judul[5:] if judul.startswith('File:') else judul
    if j.startswith('Zh-'):
        j = j[3:]
    return j.rsplit('.', 1)[0]


def periksa_judul(judul):
    """judul: senarai judul lengkap seperti 'File:Zh-wǒmen.ogg'.
    Kembalikan HANYA yang berkasnya ada, berkunci nama inti (tanpa awalan/ekstensi),
    lengkap dengan ukuran, penutur, dan lisensinya."""
    ada = {}
    for i in range(0, len(judul), 40):
        blok = judul[i:i + 40]
        d = ambil(COMMONS, {'action': 'query', 'format': 'json', 'prop': 'imageinfo',
                            'iiprop': 'size|extmetadata', 'titles': '|'.join(blok)}) or {}
        for page in d.get('query', {}).get('pages', {}).values():
            if 'imageinfo' not in page:
                continue
            ii = page['imageinfo'][0]
            em = ii.get('extmetadata', {})
            ada[inti(page['title'])] = {
                'bit': ii.get('size', 0),
                'pembuat': re.sub('<[^>]+>', '', (em.get('Artist', {}) or {}).get('value', '?')).strip(),
                'lisensi': (em.get('LicenseShortName', {}) or {}).get('value', '?')}
        time.sleep(0.3)
    return ada


d = json.load(open('app/data/hsk1.json', encoding='utf-8'))
kata = [k for p in d['pelajaran'] for k in (p.get('kata') or [])]
aksara = sorted({c for k in kata for c in k['hanzi']})
print('Kata: %d | aksara unik: %d' % (len(kata), len(aksara)))

# ---------- 1. rekaman per kata (nama apa adanya)
print()
print('=== 1. Rekaman per kata (nama berkas apa adanya) ===')
langsung = periksa_judul(['File:Zh-%s.ogg' % k['pinyin'] for k in kata])
print('ada: %d dari %d' % (len(langsung), len(kata)))

# ---------- 2. variasi nama untuk yang belum ada
print()
print('=== 2. Variasi penulisan nama berkas ===')
belum = [k for k in kata if k['pinyin'] not in langsung]
ketemu_varian = {}
for k in belum:
    calon = {VARIAN.get(k['pinyin']), k['pinyin'].replace(' ', ''), k['pinyin'].replace("'", '')} - {None}
    for v in calon:
        if v in periksa_judul(['File:Zh-%s.ogg' % v]):
            ketemu_varian[k['pinyin']] = v
            break
print('tambahan lewat variasi: %d %s' % (len(ketemu_varian), ketemu_varian))

pakai = {k['pinyin']: ketemu_varian.get(k['pinyin'], k['pinyin']) for k in kata}
semua_kata = periksa_judul(['File:Zh-%s.ogg' % n for n in sorted(set(pakai.values()))])
masih = [k for k in kata if pakai[k['pinyin']] not in semua_kata]
print('TOTAL kata berbekal rekaman: %d dari %d' % (len(kata) - len(masih), len(kata)))
print('belum ada: %s' % ' · '.join('%s %s' % (k['hanzi'], k['pinyin']) for k in masih))

# ---------- 3. rekaman per aksara
print()
print('=== 3. Rekaman per aksara ===')
pola_aksara = periksa_judul(['File:Zh-%s.ogg' % c for c in aksara])
print('pola "Zh-<aksara>.ogg": %d dari %d' % (len(pola_aksara), len(aksara)))
nama_wiktionary = {}
for i in range(0, len(aksara), 20):
    d2 = ambil(WIKTIONARY, {'action': 'query', 'format': 'json', 'prop': 'revisions', 'rvprop': 'content',
                            'rvslots': 'main', 'titles': '|'.join(aksara[i:i + 20])}) or {}
    for page in d2.get('query', {}).get('pages', {}).values():
        try:
            isi = page['revisions'][0]['slots']['main']['*']
        except Exception:
            continue
        for nm in BERKAS_AUDIO.findall(isi):
            if nm.lower().startswith(('zh-', 'cmn-')):
                nama_wiktionary.setdefault(page['title'], set()).add(inti(nm))
    time.sleep(0.3)
# Diperiksa dua kemungkinan ekstensi, karena sebagian berkas berekstensi .oga
kandidat = sorted({n for v in nama_wiktionary.values() for n in v})
ada_wikt = periksa_judul(['File:Zh-%s.ogg' % n for n in kandidat])
ada_wikt.update(periksa_judul(['File:Zh-%s.oga' % n for n in kandidat]))
aksara_beraudio = [c for c in nama_wiktionary
                   if any(n in ada_wikt for n in nama_wiktionary[c])]
print('lewat daftar audio di halaman Wiktionary: %d dari %d aksara' % (len(aksara_beraudio), len(aksara)))
print('contoh yang ada: %s' % ''.join(aksara_beraudio[:10]))

# ---------- 4. penutur, lisensi, ukuran
print()
print('=== 4. Penutur, lisensi, ukuran (rekaman kata yang akan dipakai) ===')
print('berkas: %d | total ukuran asli: %.2f MB'
      % (len(semua_kata), sum(v['bit'] for v in semua_kata.values()) / 1024 / 1024))
print('penutur :', Counter(v['pembuat'] for v in semua_kata.values()).most_common(5))
print('lisensi :', Counter(v['lisensi'] for v in semua_kata.values()).most_common(5))

# ---------- 5. tambalan dari suku kata
print()
print('=== 5. Tambalan dari rekaman suku kata ===')
semua_suku = sorted({s for v in SUKU_TAMBALAN.values() for s in v})
punya = periksa_judul(['File:Zh-%s.ogg' % s for s in semua_suku])
hilang_suku = [s for s in semua_suku if s not in punya]
print('suku kata dibutuhkan: %d | ada: %d | tidak ada: %d %s'
      % (len(semua_suku), len(punya), len(hilang_suku), hilang_suku))
print('ukuran suku kata yang ada: %.2f MB' % (sum(v['bit'] for v in punya.values()) / 1024 / 1024))
bisa = [hz for hz, s in SUKU_TAMBALAN.items() if all(x in punya for x in s)]
tidak = [hz for hz, s in SUKU_TAMBALAN.items() if not all(x in punya for x in s)]
print('kata yang bisa dibunyikan aksara-per-aksara: %d %s' % (len(bisa), bisa))
print('yang belum lengkap: %d %s' % (len(tidak), tidak))

json.dump({'kata_ada': list(semua_kata), 'masih_belum': [k['pinyin'] for k in masih],
           'varian': ketemu_varian, 'aksara_beraudio': aksara_beraudio,
           'suku_ada': list(punya), 'suku_tidak_ada': hilang_suku,
           'penutur': dict(Counter(v['pembuat'] for v in semua_kata.values())),
           'lisensi': dict(Counter(v['lisensi'] for v in semua_kata.values()))},
          open('riset-audio-hasil.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
print('hasil mentah: riset-audio-hasil.json')
