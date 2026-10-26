import datetime

def hitung_progres_program(data):
    hasil = []
    for p in data["program"]:
        terkumpul = sum(
            d["diterima"] for d in data["donasi"]
            if d["program"] == p["id"] and d["status"] == "berhasil"
        )
        persen = round(terkumpul / p["target"] * 100, 1)
        hasil.append(dict(p, terkumpul=terkumpul, persen=persen, tercapai=persen >= 100))
    return hasil

def cari_program(data, id_program):
    return next((p for p in data["program"] if p["id"] == id_program), None)

def hitung_biaya_admin(metode, jumlah):
    if metode == "qris":
        return round(jumlah * 0.007)
    elif metode == "va":
        return 4000
    elif metode == "transfer":
        return 0
    return None

def buat_entri_donasi(nomor, id_program, nama, anonim, jumlah, metode, admin, tgl=None):
    if tgl is None:
        tgl = datetime.date.today()
    return {
        "id": "DN" + str(nomor).zfill(4),
        "kuitansi": "ZIS/" + str(tgl.year) + "/" + str(tgl.month).zfill(2) + "/" + str(nomor).zfill(4),
        "program": id_program,
        "nama": nama,
        "anonim": anonim,
        "jumlah": jumlah,
        "metode": metode,
        "biaya_admin": admin,
        "diterima": jumlah - admin,
        "tanggal": tgl.isoformat(),
        "status": "berhasil"
    }

def ambil_donatur_program(data, id_program):
    hasil = []
    for d in reversed(data["donasi"]):
        if d["program"] == id_program and d["status"] == "berhasil":
            hasil.append({
                "nama": "Hamba Allah" if d["anonim"] else d["nama"],
                "jumlah": d["jumlah"],
                "tanggal": d["tanggal"]
            })
    return hasil