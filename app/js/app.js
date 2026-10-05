/* Tulis Hanzi — logika aplikasi.
   2 layar: daftar kata, dan latihan menulis satu aksara.
   Tanpa akun, tanpa server, tanpa penyimpanan progres: begitu dibuka, langsung bisa menulis.

   CARA KERJA MENULIS (dirancang supaya goresan benar tidak pernah hilang dan tidak berkedip):
     1. Pustaka Hanzi Writer dipakai sebagai PENILAI: ia yang tahu urutan, arah, dan bentuk
        goresan yang benar. Tetapi gambar "coretan mentah" milik pustaka DIMATIKAN
        (drawingColor transparan) — gambar itulah yang dulu dipudarkan pustaka sendiri setiap
        goresan selesai, sehingga tulisan yang sudah benar tampak hilang.
     2. Aplikasi menggambar sendiri pada lapisan SVG di atas kanvas (lihat buatLapisan).
        Saat pengguna menggores, lapisan ini mengungkap BENTUK ASLI goresan aksara sedikit demi
        sedikit mengikuti posisi kursor/jari (lihat gerakIsian) — jadi bukan coretan mentah,
        melainkan aksara yang terisi sesuai arah goresan yang diminta.
     3. Goresan yang BENAR dibekukan sebagai tinta dan tetap terlihat sampai tombol "Hapus"
        ditekan. Goresan yang SALAH tidak meninggalkan apa pun.
     4. Contoh arah goresan diputar DI DALAM kanvas yang sama, memakai lapisan aplikasi sendiri,
        sehingga kanvas tidak pernah dipasang ulang dan penilaian tidak pernah dibatalkan
        (pustaka membatalkan penilaian kalau animasi miliknya sendiri yang dipakai). */
(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';
  var WARNA_TINTA = '#1f2937';     // tinta hasil goresan pengguna (sama dengan strokeColor pustaka)
  var WARNA_CONTOH = '#b91c1c';    // contoh arah goresan (warna aksen aplikasi)
  var JARAK_MAKS = 300;            // kalau jari lebih jauh dari ini, isian tidak ikut bergerak
  var KORIDOR_MIN = 40;            // batas bawah setengah lebar koridor (satuan grid aksara)
  var KORIDOR_MAKS = 130;          // batas atas — diukur dari data: setengah tebal goresan terbanyak
                                   // sekitar 38 (tengah), 72 (persentil 95), 111 (tertebal)

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var state = {
    hsk1: null, strokes: null, flat: [], idx: 0,
    writer: null,
    strokeIdx: 0, total: 0, size: 0, charComplete: false, refit: false, resizeTimer: null,
    lapisan: null,      // gambar milik aplikasi: isian tinta + contoh arah
    goresAktif: null,   // goresan yang sedang ditulis pengguna
    tebal: {},          // ukuran ketebalan goresan per aksara (dihitung sekali, lalu disimpan)
    contoh: null,       // contoh arah yang sedang diputar
    generasi: 0         // penanda pemasangan kanvas; dipakai agar pemasangan lapisan yang
                        // tertunda (svg pustaka dibuat asinkron) tidak menimpa kanvas yang baru
  };

  /* ---------- data ---------- */
  function loadData() {
    if (window.__BUNDLE__) return Promise.resolve(window.__BUNDLE__); // versi satu file
    return Promise.all([
      fetch('data/hsk1.json').then(function (r) { return r.json(); }),
      fetch('data/strokes.json').then(function (r) { return r.json(); })
    ]).then(function (a) { return { hsk1: a[0], strokes: a[1] }; });
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function svgEl(tag, atr) {
    var n = document.createElementNS(NS, tag);
    for (var k in atr) { if (atr.hasOwnProperty(k)) n.setAttribute(k, atr[k]); }
    return n;
  }

  /* ---------- layar daftar ---------- */
  function renderList() {
    var box = $('#lesson-list');
    box.innerHTML = '';
    state.hsk1.pelajaran.forEach(function (pel) {
      var sec = el('section', 'lesson');
      var h = el('h2');
      h.appendChild(el('span', 'no', String(pel.id).padStart(2, '0')));
      h.appendChild(el('span', null, pel.tema));
      h.appendChild(el('span', 'count', pel.kata.length + ' kata'));
      sec.appendChild(h);

      var chips = el('div', 'chips');
      pel.kata.forEach(function (k) {
        var b = el('button', 'chip');
        b.type = 'button';
        b.appendChild(el('span', 'hzc hz', k.hanzi));
        b.appendChild(el('span', 'py', k.pinyin));
        b.title = k.hanzi + ' — ' + k.arti;
        b.addEventListener('click', function () { openByWord(pel.id, k.hanzi); });
        chips.appendChild(b);
      });
      sec.appendChild(chips);
      box.appendChild(sec);
    });
  }

  function openByWord(lessonId, hanzi) {
    var pel = state.hsk1.pelajaran.filter(function (p) { return p.id === lessonId; })[0];
    var wi = pel.kata.map(function (k) { return k.hanzi; }).indexOf(hanzi);
    openAt(state.flat.findIndex(function (f) { return f.pel.id === lessonId && f.wi === wi; }));
  }

  /* ---------- latihan ---------- */
  function current() { return state.flat[state.idx]; }

  /* data aksara yang sedang ditulis: {strokes: [bentuk asli…], medians: [garis tengah…]} */
  function dataAktif() {
    var ch = state.chars && state.chars[state.ci];
    return (ch && state.strokes[ch]) || null;
  }

  function show(screen) {
    $('#screen-list').hidden = screen !== 'list';
    $('#screen-practice').hidden = screen !== 'practice';
    window.scrollTo(0, 0);
  }

  function openAt(i) {
    state.idx = Math.max(0, Math.min(state.flat.length - 1, i));
    show('practice');
    renderPractice();
  }

  function renderPractice() {
    var f = current(), kata = f.pel.kata[f.wi];
    state.chars = Array.from(kata.hanzi);
    $('#p-crumb').textContent = 'Pelajaran ' + String(f.pel.id).padStart(2, '0') + ' · ' + f.pel.tema;
    $('#p-pinyin').textContent = kata.pinyin;
    $('#p-arti').textContent = kata.arti;
    $('#btn-prev').disabled = state.idx === 0;
    $('#btn-next').disabled = state.idx === state.flat.length - 1;
    state.ci = 0;
    renderSteps();
    mountChar();
  }

  /* petunjuk: aksara mana dari kata ini yang sedang ditulis */
  function renderSteps() {
    var box = $('#p-steps');
    box.innerHTML = '';
    state.chars.forEach(function (c, i) {
      var s = el('span', 'ch' + (i < state.ci ? ' done' : i === state.ci ? ' active' : ''), c);
      box.appendChild(s);
    });
  }

  function cellSize() {
    // ukur dari lebar dalam kartu (bukan dari section), supaya kanvas tidak pernah
    // diperas oleh kemunculan scrollbar — ukuran internal pustaka harus sama dengan ukuran tampil
    var card = $('.card');
    var avail = (card ? card.clientWidth - 32 : $('#screen-practice').clientWidth) || 320;
    return Math.max(180, Math.min(avail, 340));
  }

  function hint(teks, bagus) {
    var h = $('#p-hint');
    h.textContent = teks;
    h.className = bagus ? 'hintline good' : 'hintline';
  }

  /* memasang kanvas untuk aksara yang sedang dikerjakan */
  function mountChar(forceSize, pesan) {
    var ch = state.chars[state.ci];
    var size = forceSize || cellSize();
    var target = $('#hw');
    target.innerHTML = '';
    $('#cell').style.width = size + 'px';
    $('#cell').style.height = size + 'px';
    state.size = size;
    state.strokeIdx = 0;
    state.charComplete = false;
    state.total = (state.strokes[ch] && state.strokes[ch].strokes.length) || 0;
    state.goresAktif = null;
    state.contoh = null;
    state.generasi += 1;
    state.lapisan = null;
    $('#p-next-char').hidden = true;              // tombol lanjut hanya muncul setelah aksara selesai
    hint(pesan || ('Jiplak aksara ' + ch + ' mengikuti contoh. Goresan yang salah tidak akan diterima.'));
    renderDots();

    state.writer = HanziWriter.create(target, ch, {
      width: size, height: size, padding: Math.round(size * 0.04),
      // PENTING: showCharacter harus false. Kalau aksara aslinya tampil sejak awal, tidak ada
      // yang menggantikan goresan pengguna saat pustaka memudarkannya. Dengan false, yang tampil
      // hanya garis tepi kosong, dan tintanya diisi oleh lapisan aplikasi sendiri (lihat buatLapisan).
      showCharacter: false,
      showOutline: true,
      strokeColor: WARNA_TINTA,       // goresan benar versi pustaka (mengisi aksara)
      outlineColor: '#ded3c0',        // garis tepi template
      radicalColor: null,
      // Coretan mentah pustaka dimatikan: aplikasi menggambar isian aksara sendiri.
      // Ini sekaligus menghapus kedipan (coretan mentah muncul lalu dipudarkan) dan masalah
      // gambar goresan yang ditolak ikut tertinggal di kanvas.
      drawingColor: 'rgba(0,0,0,0)',
      drawingWidth: Math.round(size * 0.085),
      highlightColor: '#f2b705',
      strokeAnimationSpeed: 1,
      delayBetweenStrokes: 220,
      charDataLoader: function (c, onComplete) {
        var d = state.strokes[c];
        if (d) onComplete(d); else onComplete({ strokes: [], medians: [] });
      }
    });

    // jaring pengaman: ukuran kotak tampil harus sama dengan ukuran internal pustaka.
    // Kalau masih berbeda (mis. tata letak digeser sesuatu di luar dugaan), ulangi sekali
    // dengan ukuran nyata — supaya gambar selalu jatuh tepat di bawah jari.
    if (!state.refit) {
      var shown = $('#hw').getBoundingClientRect().width;
      if (shown > 100 && Math.abs(shown - size) > 2) {
        state.refit = true;
        mountChar(Math.round(shown), pesan);
        state.refit = false;
        return;
      }
    }
    pasangLapisanSaatSiap(state.generasi);
    startQuiz();
  }

  /* Lapisan gambar dipasang setelah svg pustaka benar-benar ada.
     PENTING: HanziWriter.create() membangun svg-nya SECARA ASINKRON (setelah data aksara selesai
     dimuat), jadi saat mountChar selesai pun #hw bisa masih kosong. Kalau lapisan dipasang
     sebelum svg-nya ada, lapisan itu tidak pernah tampil — pengguna merasa tidak bisa menulis. */
  function pasangLapisanSaatSiap(generasi) {
    var coba = 0;
    (function cek() {
      if (generasi !== state.generasi) return;      // kanvas sudah dipasang ulang: batalkan
      buatLapisan();
      if (state.lapisan) { mainkanContoh(false); return; }
      if (++coba < 100) setTimeout(cek, 50);
    })();
  }

  function startQuiz() {
    state.writer.quiz({
      showHintAfterMisses: 2,        // setelah 2 kali salah, goresan berikutnya ditunjukkan
      highlightOnComplete: true,
      onCorrectStroke: function (d) {
        bekukanIsian();
        state.strokeIdx = (typeof d.strokeNum === 'number' ? d.strokeNum + 1 : state.strokeIdx + 1);
        renderDots();
      },
      onMistake: function () {
        kosongkanIsian();
        var c = $('#cell');
        c.classList.add('miss');
        setTimeout(function () { c.classList.remove('miss'); }, 420);
      },
      onComplete: function () { charDone(); }
    });
  }

  function renderDots() {
    var box = $('#p-dots');
    box.innerHTML = '';
    for (var i = 0; i < state.total; i++) {
      box.appendChild(el('i', i < state.strokeIdx ? 'on' : null));
    }
  }

  /* satu aksara selesai — TANPA menghapus dan TANPA pindah otomatis.
     Tinta tetap seperti yang ditulis; pengguna yang menentukan langkah berikutnya. */
  function charDone() {
    state.charComplete = true;
    var cell = $('#cell');
    cell.classList.add('win');
    setTimeout(function () { cell.classList.remove('win'); }, 1400);

    if (state.ci >= state.chars.length - 1) {
      hint('Selesai — seluruh aksara kata ini sudah ditulis. Tekan "Berikutnya" untuk kata selanjutnya, atau "Hapus" untuk mengulang.', true);
      $('#p-next-char').hidden = true;
      return;
    }
    $('#btn-next-char').textContent = 'Aksara berikutnya (' + state.chars[state.ci + 1] + ') →';
    $('#p-next-char').hidden = false;
    hint('Aksara ' + state.chars[state.ci] + ' selesai — goresanmu tetap tersimpan. Lanjut kapan saja.', true);
  }

  /* ================= lapisan gambar milik aplikasi ================= */
  /* Isinya:
       gSelesai : goresan yang sudah diterima — bentuk asli aksara, tinta penuh (beku)
       isian    : goresan yang sedang ditulis — bentuk asli aksara, diungkap sebagian lewat
                  "koridor" (clipPath) yang tumbuh mengikuti posisi jari/kursor
       contoh   : contoh arah goresan (jalur kuas + titik ujung), diputar di dalam kanvas
     Semua koordinat memakai satuan data aksara (grid 1024, sumbu-y ke atas). Transformasi
     grid->piksel diambil LANGSUNG dari svg milik pustaka, jadi gambar aplikasi jatuh persis
     di atas gambar pustaka berapa pun ukuran kanvasnya. */
  function buatLapisan() {
    var svgLib = $('#hw svg');
    if (!svgLib) return;
    var ubah = transformasi(svgLib);
    if (!ubah) return;

    var L = {};
    L.ubah = ubah;
    L.svg = svgEl('svg', { 'class': 'lapisan-tinta' });
    var defs = svgEl('defs');
    L.klip = svgEl('clipPath', { id: 'klip-isian', clipPathUnits: 'userSpaceOnUse' });
    L.koridor = svgEl('path', { id: 'koridor', d: '' });
    L.klip.appendChild(L.koridor);
    defs.appendChild(L.klip);
    L.svg.appendChild(defs);

    L.lapis = svgEl('g', { transform: ubah.teks });
    L.gSelesai = svgEl('g', { 'class': 'selesai' });
    L.isian = svgEl('path', { 'class': 'isian', d: '', fill: WARNA_TINTA, 'clip-path': 'url(#klip-isian)' });
    L.contoh = svgEl('path', {
      'class': 'contoh-arah', d: '', fill: 'none', stroke: WARNA_CONTOH,
      'stroke-width': 140, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: '.5'
    });
    L.titik = svgEl('circle', { 'class': 'contoh-titik', cx: 0, cy: 0, r: 38, fill: WARNA_CONTOH, opacity: 0 });
    L.lapis.appendChild(L.gSelesai);
    L.lapis.appendChild(L.isian);
    L.lapis.appendChild(L.contoh);
    L.lapis.appendChild(L.titik);
    L.svg.appendChild(L.lapis);
    $('#hw').appendChild(L.svg);
    state.lapisan = L;
  }

  /* transformasi grid->piksel dibaca dari svg pustaka (translate + scale) */
  function transformasi(svgLib) {
    var g = svgLib && svgLib.querySelector('g[transform]');
    if (!g) return null;
    var m = /translate\(\s*([-\d.]+)[ ,]+([-\d.]+)\s*\)\s*scale\(\s*([-\d.]+)[ ,]+([-\d.]+)\s*\)/
      .exec(g.getAttribute('transform') || '');
    if (!m) return null;
    return {
      tx: +m[1], ty: +m[2], sx: +m[3], sy: +m[4],
      teks: 'translate(' + m[1] + ', ' + m[2] + ') scale(' + m[3] + ', ' + m[4] + ')'
    };
  }

  /* konversi posisi kursor/jari -> satuan grid aksara */
  function keGrid(e) {
    var L = state.lapisan;
    if (!L) return null;
    var r = L.svg.getBoundingClientRect();
    return [(e.clientX - r.left - L.ubah.tx) / L.ubah.sx,
            (e.clientY - r.top - L.ubah.ty) / L.ubah.sy];
  }

  /* ---------- hitungan garis tengah goresan ---------- */
  function kumulatif(titik) {
    var k = [0];
    for (var i = 1; i < titik.length; i++) {
      k.push(k[i - 1] + Math.hypot(titik[i][0] - titik[i - 1][0], titik[i][1] - titik[i - 1][1]));
    }
    return k;
  }

  /* titik terdekat pada garis tengah + panjang garis sampai titik itu */
  function proyeksi(titik, k, p) {
    var hasil = { jarak: Infinity, panjang: 0 };
    for (var i = 1; i < titik.length; i++) {
      var a = titik[i - 1], b = titik[i];
      var vx = b[0] - a[0], vy = b[1] - a[1];
      var p2 = vx * vx + vy * vy || 1;
      var t = Math.max(0, Math.min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / p2));
      var qx = a[0] + t * vx, qy = a[1] + t * vy;
      var d = Math.hypot(p[0] - qx, p[1] - qy);
      if (d < hasil.jarak) hasil = { jarak: d, panjang: k[i - 1] + t * Math.sqrt(p2) };
    }
    return hasil;
  }

  /* salinan garis tengah sampai panjang tertentu */
  function potong(titik, k, panjang) {
    var hasil = [titik[0]];
    for (var i = 1; i < titik.length; i++) {
      if (k[i] <= panjang) { hasil.push(titik[i]); continue; }
      var t = (panjang - k[i - 1]) / (k[i] - k[i - 1] || 1);
      hasil.push([titik[i - 1][0] + t * (titik[i][0] - titik[i - 1][0]),
                  titik[i - 1][1] + t * (titik[i][1] - titik[i - 1][1])]);
      break;
    }
    return hasil;
  }

  /* titik pada garis tengah sejauh panjang tertentu (untuk titik ujung contoh) */
  function diPanjang(titik, k, panjang) {
    if (panjang <= 0) return titik[0];
    for (var i = 1; i < titik.length; i++) {
      if (k[i] >= panjang) {
        var t = (panjang - k[i - 1]) / (k[i] - k[i - 1] || 1);
        return [titik[i - 1][0] + t * (titik[i][0] - titik[i - 1][0]),
                titik[i - 1][1] + t * (titik[i][1] - titik[i - 1][1])];
      }
    }
    return titik[titik.length - 1];
  }

  /* Pita isian: gabungan potongan selebar ketebalan goresan di sepanjang garis tengah.
     Bentuknya mengikuti arah goresan — jadi bagian aksara yang "terbuka" tidak melompat jauh
     melewati posisi jari (itu yang membuat isian terasa presisi, bukan sekadar mekar). */
  function pita(titik, setengah) {
    if (titik.length < 2) return '';
    // pangkal: satu titik tambahan di belakang titik pertama, supaya pangkal goresan (yang
    // bentuknya menonjol ke belakang) ikut terbuka — kalau tidak, ada sisa yang tak pernah terisi
    var d0x = titik[0][0] - titik[1][0], d0y = titik[0][1] - titik[1][1];
    var d0l = Math.hypot(d0x, d0y) || 1;
    titik = [[titik[0][0] + d0x / d0l * setengah * 0.9, titik[0][1] + d0y / d0l * setengah * 0.9]].concat(titik);
    var kiri = [], kanan = [], i, dx, dy, L, nx, ny;
    for (i = 0; i < titik.length; i++) {
      var p0 = titik[Math.max(0, i - 1)];
      var p1 = titik[i];
      var p2 = titik[Math.min(titik.length - 1, i + 1)];
      dx = p2[0] - p0[0]; dy = p2[1] - p0[1];
      L = Math.hypot(dx, dy) || 1;
      nx = -dy / L * setengah; ny = dx / L * setengah;
      kiri.push([p1[0] + nx, p1[1] + ny]);
      kanan.push([p1[0] - nx, p1[1] - ny]);
    }
    var angka = function (p) { return p[0].toFixed(1) + ' ' + p[1].toFixed(1); };
    var jalur = [];
    for (i = 1; i < titik.length; i++) {
      // potongan memakai titik sudut bersama, jadi sambungan antar-potongan tidak berlubang
      jalur.push('M ' + angka(kiri[i - 1]) + ' L ' + angka(kiri[i]) +
                 ' L ' + angka(kanan[i]) + ' L ' + angka(kanan[i - 1]) + ' Z');
    }
    // ujung depan dibulatkan (cakram selebar ketebalan goresan). Dulu ujungnya dipotong lurus
    // sehingga terlihat seperti gambar yang terpotong, bukan seperti kuas yang sedang berjalan.
    // Arah putaran cakram disamakan dengan potongan-potongan di atas supaya isian tidak berlubang.
    var ujung = titik[titik.length - 1], bulat = [], jariUjung = setengah * 0.5;
    for (var j = 0; j < 16; j++) {
      var a = -2 * Math.PI * j / 16;
      bulat.push([ujung[0] + jariUjung * Math.cos(a), ujung[1] + jariUjung * Math.sin(a)]);
    }
    jalur.push('M ' + bulat.map(angka).join(' L ') + ' Z');
    return jalur.join(' ');
  }

  /* ---------- ukuran koridor isian, diukur dari bentuk asli goresan ---------- */
  /* ubah path bentuk asli (M/L/Q) menjadi daftar titik tepi, lengkung Q diratakan */
  function tepiPath(path) {
    var tok = String(path).match(/[MLQZmlqz]|-?\d+\.?\d*/g) || [];
    var titik = [], i = 0, akhir = null, j, u;
    while (i < tok.length) {
      var t = tok[i];
      if (t === 'M' || t === 'L') {
        akhir = [+tok[i + 1], +tok[i + 2]];
        titik.push(akhir); i += 3;
      } else if (t === 'Q') {
        var c = [+tok[i + 1], +tok[i + 2]], p1 = [+tok[i + 3], +tok[i + 4]];
        for (j = 1; j <= 12; j++) {
          u = j / 12;
          titik.push([
            (1 - u) * (1 - u) * akhir[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0],
            (1 - u) * (1 - u) * akhir[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1]
          ]);
        }
        akhir = p1; i += 5;
      } else { i += 1; }
    }
    return titik;
  }

  function jarakKeGaris(p, garis) {
    var terbaik = Infinity;
    for (var i = 1; i < garis.length; i++) {
      var a = garis[i - 1], b = garis[i];
      var vx = b[0] - a[0], vy = b[1] - a[1];
      var p2 = vx * vx + vy * vy || 1;
      var t = Math.max(0, Math.min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / p2));
      var d = Math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy));
      if (d < terbaik) terbaik = d;
    }
    return terbaik;
  }

  /* Setengah lebar koridor untuk tiap goresan = jarak terjauh dari garis tengah ke tepi bentuk
     asli goresan itu, ditambah sedikit. Dihitung dari data, bukan angka tetap: angka tetap
     membuat koridor terlalu gemuk pada goresan pendek (seluruh goresan langsung terlihat semua)
     atau terlalu sempit pada goresan besar (bentuk aksara terpotong di pinggirnya). */
  function tebalGoresan(ch) {
    if (state.tebal[ch]) return state.tebal[ch];
    var d = state.strokes[ch], hasil = [];
    for (var i = 0; i < d.strokes.length; i++) {
      var tepi = tepiPath(d.strokes[i]);
      var med = (d.medians[i] || []).map(function (p) { return [p[0], p[1]]; });
      var maks = 0, j;
      for (j = 0; j < tepi.length; j++) maks = Math.max(maks, jarakKeGaris(tepi[j], med));
      hasil.push(Math.max(KORIDOR_MIN, Math.min(KORIDOR_MAKS, maks * 1.15)));
    }
    state.tebal[ch] = hasil;
    return hasil;
  }

  function penggunaMenulis() { return !!state.goresAktif; }

  /* pengguna mulai menggores: siapkan bentuk asli goresan yang sedang diminta */
  function mulaiIsian() {
    var d = dataAktif(), L = state.lapisan;
    if (!d || !L || !d.medians || !d.strokes) return;
    if (state.charComplete || state.strokeIdx >= d.medians.length) return;
    hentikanContoh();
    var ch = state.chars[state.ci];
    var med = d.medians[state.strokeIdx].slice();
    var k = kumulatif(med);
    state.goresAktif = {
      median: med, k: k, total: k[k.length - 1], panjang: 0,
      setengah: tebalGoresan(ch)[state.strokeIdx] || KORIDOR_MIN
    };
    L.isian.setAttribute('d', d.strokes[state.strokeIdx]);   // bentuk asli aksara
    L.isian.setAttribute('clip-path', 'url(#klip-isian)');
    L.koridor.setAttribute('d', '');
  }

  /* pengguna menggores: isian diungkap sampai posisi kursor/jari.
     Panjang yang sudah terisi TIDAK PERNAH mundur — itu yang membuat gambarnya tenang (tanpa kedip). */
  function gerakIsian(e) {
    var s = state.goresAktif, L = state.lapisan;
    if (!s || !L) return;
    var p = keGrid(e);
    if (!p) return;
    var pos = proyeksi(s.median, s.k, p);
    if (pos.jarak > JARAK_MAKS) return;                 // jari jauh dari goresan yang diminta
    if (pos.panjang <= s.panjang + 1) return;           // tidak mundur
    s.panjang = pos.panjang;
    L.koridor.setAttribute('d', pita(potong(s.median, s.k, s.panjang), s.setengah,
                                     s.panjang >= s.total * 0.995));
  }

  /* goresan benar: isian dibekukan menjadi tinta yang tidak pernah hilang */
  function bekukanIsian() {
    var L = state.lapisan;
    state.goresAktif = null;
    if (!L) return;
    L.koridor.setAttribute('d', '');
    if (L.isian.getAttribute('d')) {
      L.isian.removeAttribute('clip-path');       // tampil penuh, bukan sebagian
      L.isian.setAttribute('class', 'isian selesai');
      L.gSelesai.appendChild(L.isian);            // pindah ke lapisan tinta menetap
      L.isian = svgEl('path', { 'class': 'isian', d: '', fill: WARNA_TINTA, 'clip-path': 'url(#klip-isian)' });
      L.lapis.insertBefore(L.isian, L.contoh);
    }
  }

  /* goresan salah: tidak meninggalkan apa pun */
  function kosongkanIsian() {
    var L = state.lapisan;
    state.goresAktif = null;
    if (!L) return;
    L.koridor.setAttribute('d', '');
    L.isian.setAttribute('d', '');
  }

  /* ---------- contoh arah goresan, diputar DI DALAM kanvas ---------- */
  /* Menghentikan contoh yang sedang berjalan SEKALIGUS animasinya. Kalau hanya state-nya yang
     dikosongkan, animasi lama tetap berjalan dan menimpa animasi baru (bug ini pernah terjadi:
     tombol "Lihat contoh" terlihat tidak bekerja karena animasi lama yang menulis ulang). */
  function hentikanContoh() {
    var s = state.contoh;
    state.contoh = null;
    if (s) {
      s.jalan = false;
      if (s.animasi && s.animasi.stop) s.animasi.stop();
      if (s.jeda) clearTimeout(s.jeda);
    }
    var L = state.lapisan;
    if (!L) return;
    L.contoh.setAttribute('d', '');
    L.titik.setAttribute('opacity', 0);
  }

  /* menjalankan animasi berbasis waktu (0..1). Memakai requestAnimationFrame, TETAPI dengan
     cadangan timer: sebagian browser/lingkungan tidak pernah memanggil rAF (mis. jendela tanpa
     gambar), dan contoh arah goresan tidak boleh ikut berhenti hanya karena itu. */
  function jalankanAnimasi(durasi, perbarui, selesai) {
    var mulai = 0, tik = 0, cadangan = false, henti = false;
    var perkiraanLangkah = Math.max(6, Math.round(durasi / 33));   // cadangan berbasis jumlah frame
    var jam = function () {
      return (window.performance && performance.now) ? performance.now() : Date.now();
    };
    var langkah = function (sekarang) {
      if (henti) return;
      if (!mulai) mulai = sekarang - 1;
      var berdasarkanWaktu = (sekarang - mulai) / durasi;
      // dipakai yang lebih maju: waktu, atau jumlah frame. Sebagian lingkungan (mis. jendela
      // tanpa gambar) tidak memajukan jam, dan animasi tidak boleh ikut berhenti karena itu.
      var f = Math.min(1, Math.max(berdasarkanWaktu, tik / perkiraanLangkah));
      perbarui(f);
      tik += 1;
      if (f >= 1) { henti = true; selesai(); return; }
      if (cadangan) setTimeout(function () { langkah(jam()); }, 33);
      else window.requestAnimationFrame(langkah);
    };
    window.requestAnimationFrame(langkah);
    setTimeout(function () {
      if (tik < 2 && !henti) { cadangan = true; langkah(jam()); }
    }, 260);
    return { stop: function () { henti = true; } };
  }

  /* semua=true: putar sampai goresan terakhir. semua=false: hanya goresan yang diminta sekarang. */
  function mainkanContoh(semua) {
    var d = dataAktif(), L = state.lapisan;
    hentikanContoh();
    if (!d || !L || !d.medians.length) return;
    var mulai = Math.min(state.strokeIdx, d.medians.length - 1);
    var akhir = semua ? d.medians.length - 1 : mulai;
    var sesi = { jalan: true, animasi: null, jeda: null };
    state.contoh = sesi;

    var jalanSatu = function (i) {
      if (!sesi.jalan) return;
      var med = d.medians[i];
      var k = kumulatif(med);
      var total = k[k.length - 1] || 1;
      L.contoh.setAttribute('d', 'M ' + med.map(function (p) { return p[0] + ' ' + p[1]; }).join(' L '));
      L.contoh.setAttribute('stroke-dasharray', total + ' ' + total);
      L.contoh.setAttribute('stroke-dashoffset', total);
      sesi.animasi = jalankanAnimasi(
        Math.max(420, Math.min(1100, total * 1.6)),
        function (f) {
          if (!sesi.jalan) return;
          L.contoh.setAttribute('stroke-dashoffset', total * (1 - f));
          var ujung = diPanjang(med, k, total * f);
          L.titik.setAttribute('cx', ujung[0]); L.titik.setAttribute('cy', ujung[1]);
          L.titik.setAttribute('opacity', .85);
        },
        function () {
          if (!sesi.jalan) return;
          L.titik.setAttribute('opacity', 0);
          if (i < akhir) { sesi.jeda = setTimeout(function () { jalanSatu(i + 1); }, 170); }
          else { sesi.jalan = false; }
        }
      );
    };
    jalanSatu(mulai);
  }

  /* ---------- tombol ---------- */
  function wire() {
    $('#btn-back').addEventListener('click', function () { show('list'); });

    // contoh arah goresan diputar di kanvas latihan (bukan di kotak terpisah)
    $('#btn-demo').addEventListener('click', function () { mainkanContoh(true); });

    // menggores dipantau lewat event yang sama seperti yang dipakai pustaka
    ['mousedown', 'touchstart'].forEach(function (ev) {
      $('#hw').addEventListener(ev, function () { mulaiIsian(); }, true);
    });
    ['mousemove', 'touchmove'].forEach(function (ev) {
      $('#hw').addEventListener(ev, function (e) {
        if (penggunaMenulis()) gerakIsian(e.touches ? e.touches[0] : e);
      }, true);
    });

    // mengulang aksara aktif — satu-satunya cara tinta dihapus selain pindah kata
    $('#btn-clear').addEventListener('click', function () { mountChar(); });

    // lanjut ke aksara berikutnya, hanya bisa ditekan setelah aksara ini selesai
    $('#btn-next-char').addEventListener('click', function () {
      if (!state.charComplete || state.ci >= state.chars.length - 1) return;
      state.ci += 1;
      renderSteps();
      mountChar();
    });

    $('#btn-prev').addEventListener('click', function () { if (state.idx > 0) openAt(state.idx - 1); });
    $('#btn-next').addEventListener('click', function () { if (state.idx < state.flat.length - 1) openAt(state.idx + 1); });

    // Hanya pasang ulang kanvas kalau LEBARNA berubah CUKUP BANYAK (mis. HP diputar).
    // Toleransi 16 px disengaja: perubahan kecil — address bar HP yang menutup saat menggulir,
    // scrollbar desktop yang muncul, gejolak tata letak — TIDAK boleh menghapus tulisan.
    // Lebih baik tinta sedikit melenceng daripada tulisan pengguna hilang.
    window.addEventListener('resize', function () {
      clearTimeout(state.resizeTimer);
      state.resizeTimer = setTimeout(function () {
        if ($('#screen-practice').hidden) return;
        var target = cellSize();
        if (Math.abs(target - state.size) <= 16) return;
        mountChar(target, 'Ukuran layar berubah cukup banyak, jadi kanvas dibuat ulang. Aksara ini perlu ditulis lagi.');
      }, 250);
    });
  }

  /* ---------- mulai ---------- */
  loadData().then(function (d) {
    state.hsk1 = d.hsk1;
    state.strokes = d.strokes;
    state.flat = [];
    d.hsk1.pelajaran.forEach(function (pel) {
      pel.kata.forEach(function (k, wi) { state.flat.push({ pel: pel, wi: wi, kata: k }); });
    });
    $('#meta-kata').textContent = String(d.hsk1.meta.jumlah_kata);
    renderList();
    wire();
    show('list');
    if ('serviceWorker' in navigator && location.protocol !== 'file:') {
      navigator.serviceWorker.register('sw.js').catch(function () { /* offline tetap jalan dari cache browser */ });
    }
    window.tulisHanzi = state;   // dibuka untuk keperluan uji & debug di konsol browser
  }).catch(function (err) {
    $('#lesson-list').innerHTML =
      '<p class="lead">Data gagal dimuat: ' + err.message + '<br>Jalankan lewat server lokal (bukan klik dua kali), mis. <code>python -m http.server</code>.</p>';
  });
})();
