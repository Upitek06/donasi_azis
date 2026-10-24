from flask import Blueprint, request, render_template_string
import datetime
from services import (
    baca_data, simpan_data,
    hitung_biaya_admin, buat_entri_donasi, hitung_progres_program,
    hitung_zakat_penghasilan, hitung_zakat_maal, rekap_laporan_bulanan
)

web_bp = Blueprint("web", __name__)

CSS = "<style>body{font-family:'Trebuchet MS';margin:30px;max-width:820px;color:#123} .bar{background:#e5efe8;height:14px;border-radius:7px} .isi{background:#1f7a4d;height:14px;border-radius:7px} .p{border:1px solid #cde;padding:12px;margin:10px 0;border-radius:8px} nav a{margin-right:14px}</style>"
NAV = "<nav><a href='/'>Program</a><a href='/kalkulator'>Kalkulator Zakat</a><a href='/laporan'>Laporan</a></nav>"


@web_bp.route("/")
def index():
    data = baca_data()
    html = "<html><head><title>Donasi ZIS</title>" + CSS + "</head><body>" + NAV + "<h1>Program Kebaikan</h1>"
    for p in hitung_progres_program(data):
        lebar = 100 if p["persen"] > 100 else p["persen"]
        html += "<div class='p'><b>" + p["nama"] + "</b> <small>(" + p["jenis"] + ")</small><br>Rp " + "{:,}".format(p["terkumpul"]).replace(",", ".") + " dari Rp " + "{:,}".format(p["target"]).replace(",", ".")
        html += " · " + str(p["persen"]) + "%<div class='bar'><div class='isi' style='width:" + str(lebar) + "%'></div></div><a href='/donasi/" + p["id"] + "'>Donasi</a></div>"
    return html + "</body></html>"


@web_bp.route("/donasi/<id_program>", methods=["GET", "POST"])
def donasi(id_program):
    data = baca_data()
    program = next((p for p in data["program"] if p["id"] == id_program), None)
    if program is None:
        return "Program tidak ditemukan", 404
    pesan = ""
    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        anonim = request.form.get("anonim") == "on"
        metode = request.form.get("metode", "")
        try:
            jumlah = int(request.form.get("jumlah", "0"))
        except ValueError:
            jumlah = 0
        admin = hitung_biaya_admin(metode, jumlah)
        if jumlah < 10000:
            pesan = "Donasi minimal Rp 10.000"
        elif admin is None:
            pesan = "Metode pembayaran tidak dikenal"
        elif nama == "" and not anonim:
            pesan = "Nama wajib diisi (atau centang anonim)"
        else:
            nomor = len(data["donasi"]) + 1
            baru = buat_entri_donasi(nomor, id_program, nama, anonim, jumlah, metode, admin)
            data["donasi"].append(baru)
            simpan_data(data)
            pesan = "Jazakallahu khairan. Kuitansi " + baru["kuitansi"] + ", diterima program Rp " + "{:,}".format(baru["diterima"]).replace(",", ".")
    donatur = ""
    for d in reversed(data["donasi"]):
        if d["program"] == id_program and d["status"] == "berhasil":
            donatur += "<li>" + ("Hamba Allah" if d["anonim"] else d["nama"]) + " — Rp " + "{:,}".format(d["jumlah"]).replace(",", ".") + "</li>"
    return render_template_string("<html><head>" + CSS + "</head><body>" + NAV + """<h1>{{ p.nama }}</h1><p><b>{{ pesan }}</b></p>
    <form method="post">Nama <input name="nama"> <label><input type="checkbox" name="anonim"> sembunyikan nama</label><br>
    Jumlah <input type="number" name="jumlah"> Metode <select name="metode"><option value="qris">QRIS (0,7%)</option><option value="transfer">Transfer bank</option><option value="va">Virtual account (Rp 4.000)</option></select>
    <button>Tunaikan</button></form><h3>Donatur terbaru</h3><ul>""" + donatur + "</ul></body></html>", p=program, pesan=pesan)


@web_bp.route("/kalkulator", methods=["GET", "POST"])
def kalkulator():
    data = baca_data()
    harga_emas = data["pengaturan"]["harga_emas_per_gram"]
    hasil = ""
    if request.method == "POST":
        jenis = request.form.get("jenis")
        try:
            a = int(request.form.get("a") or 0)
            b = int(request.form.get("b") or 0)
            c = int(request.form.get("c") or 0)
        except ValueError:
            a = b = c = 0
        if jenis == "penghasilan":
            nisab, wajib, zakat = hitung_zakat_penghasilan(a + b, harga_emas)
            if wajib:
                hasil = "Wajib zakat: Rp " + "{:,}".format(zakat).replace(",", ".") + " per bulan"
            else:
                hasil = "Belum wajib zakat (nisab Rp " + "{:,}".format(nisab).replace(",", ".") + " per bulan)"
        else:
            haul = request.form.get("haul") == "on"
            nisab, wajib, _, zakat = hitung_zakat_maal(a + b - c, harga_emas, haul)
            if wajib:
                hasil = "Wajib zakat maal: Rp " + "{:,}".format(zakat).replace(",", ".")
            else:
                hasil = "Belum wajib zakat maal (nisab Rp " + "{:,}".format(nisab).replace(",", ".") + ", harus genap 1 tahun)"
    return render_template_string("<html><head>" + CSS + "</head><body>" + NAV + """<h1>Kalkulator Zakat</h1><p>Harga emas: Rp {{ emas }}/gram</p><p><b>{{ hasil }}</b></p>
    <div class="p"><h3>Zakat penghasilan</h3><form method="post"><input type="hidden" name="jenis" value="penghasilan">Gaji/bulan <input name="a"> Pendapatan lain <input name="b"> <button>Hitung</button></form></div>
    <div class="p"><h3>Zakat maal</h3><form method="post"><input type="hidden" name="jenis" value="maal">Tabungan & investasi <input name="a"> Emas (Rp) <input name="b"> Utang jatuh tempo <input name="c">
    <label><input type="checkbox" name="haul"> sudah 1 tahun</label> <button>Hitung</button></form></div></body></html>""",
                                  emas="{:,}".format(harga_emas).replace(",", "."), hasil=hasil)


@web_bp.route("/laporan")
def laporan():
    data = baca_data()
    bulan = request.args.get("bulan", datetime.date.today().strftime("%Y-%m"))
    per_jenis, _, _ = rekap_laporan_bulanan(data, bulan)
    baris = "".join("<li>" + j.capitalize() + ": Rp " + "{:,}".format(v).replace(",", ".") + "</li>" for j, v in per_jenis.items())
    return "<html><head>" + CSS + "</head><body>" + NAV + "<h1>Laporan " + bulan + "</h1><ul>" + (baris or "<li>Belum ada donasi</li>") + "</ul></body></html>"