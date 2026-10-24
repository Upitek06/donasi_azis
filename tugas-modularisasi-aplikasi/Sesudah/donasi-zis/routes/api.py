from flask import Blueprint, request, jsonify
import datetime
from services import (
    baca_data, simpan_data,
    hitung_biaya_admin, buat_entri_donasi, hitung_progres_program,
    hitung_zakat_penghasilan, hitung_zakat_maal, rekap_laporan_bulanan
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/program")
def api_program():
    data = baca_data()
    return jsonify(hitung_progres_program(data))


@api_bp.route("/donasi", methods=["POST"])
def api_donasi():
    data = baca_data()
    b = request.get_json(silent=True) or {}
    program = next((p for p in data["program"] if p["id"] == b.get("program")), None)
    if program is None:
        return jsonify({"error": "Program tidak ditemukan"}), 404
    jumlah = b.get("jumlah")
    if not isinstance(jumlah, int) or jumlah < 10000:
        return jsonify({"error": "Donasi minimal Rp 10.000"}), 400
    metode = b.get("metode")
    admin = hitung_biaya_admin(metode, jumlah)
    if admin is None:
        return jsonify({"error": "Metode pembayaran tidak dikenal"}), 400
    nama = str(b.get("nama", "")).strip()
    anonim = bool(b.get("anonim", False))
    if nama == "" and not anonim:
        return jsonify({"error": "Nama wajib diisi (atau pilih anonim)"}), 400
    tgl = datetime.date.fromisoformat(b["tanggal"]) if b.get("tanggal") else datetime.date.today()
    nomor = len(data["donasi"]) + 1
    baru = buat_entri_donasi(nomor, program["id"], nama, anonim, jumlah, metode, admin, tgl)
    data["donasi"].append(baru)
    simpan_data(data)
    return jsonify(baru), 201


@api_bp.route("/program/<id_program>/donatur")
def api_donatur(id_program):
    data = baca_data()
    hasil = []
    for d in reversed(data["donasi"]):
        if d["program"] == id_program and d["status"] == "berhasil":
            hasil.append({
                "nama": "Hamba Allah" if d["anonim"] else d["nama"],
                "jumlah": d["jumlah"],
                "tanggal": d["tanggal"]
            })
    return jsonify(hasil)


@api_bp.route("/zakat/penghasilan", methods=["POST"])
def api_zakat_penghasilan():
    data = baca_data()
    b = request.get_json(silent=True) or {}
    total = b.get("gaji", 0) + b.get("pendapatan_lain", 0)
    nisab, wajib, zakat = hitung_zakat_penghasilan(total, data["pengaturan"]["harga_emas_per_gram"])
    return jsonify({"penghasilan": total, "nisab_bulanan": nisab, "wajib": wajib, "zakat": zakat})


@api_bp.route("/zakat/maal", methods=["POST"])
def api_zakat_maal():
    data = baca_data()
    b = request.get_json(silent=True) or {}
    bersih = b.get("tabungan", 0) + b.get("emas", 0) + b.get("investasi", 0) - b.get("utang", 0)
    nisab, wajib, alasan, zakat = hitung_zakat_maal(
        bersih, data["pengaturan"]["harga_emas_per_gram"], b.get("haul", False)
    )
    if not wajib:
        return jsonify({"harta_bersih": bersih, "nisab": nisab, "wajib": False, "alasan": alasan, "zakat": 0})
    return jsonify({"harta_bersih": bersih, "nisab": nisab, "wajib": True, "zakat": zakat})


@api_bp.route("/pengaturan/emas", methods=["POST"])
def api_harga_emas():
    data = baca_data()
    harga = (request.get_json(silent=True) or {}).get("harga_emas_per_gram")
    if not isinstance(harga, int) or harga <= 0:
        return jsonify({"error": "Harga emas harus bilangan bulat > 0"}), 400
    data["pengaturan"]["harga_emas_per_gram"] = harga
    simpan_data(data)
    return jsonify(data["pengaturan"])


@api_bp.route("/laporan")
def api_laporan():
    data = baca_data()
    bulan = request.args.get("bulan", datetime.date.today().strftime("%Y-%m"))
    per_jenis, admin, donatur = rekap_laporan_bulanan(data, bulan)
    return jsonify({
        "bulan": bulan,
        "per_jenis": per_jenis,
        "total": sum(per_jenis.values()),
        "total_biaya_admin": admin,
        "jumlah_donasi": donatur
    })