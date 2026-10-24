import datetime

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

def hitung_zakat_penghasilan(total, harga_emas):
    nisab = round(85 * harga_emas / 12)
    wajib = total >= nisab
    zakat = round(total * 0.025) if wajib else 0
    return nisab, wajib, zakat

def hitung_zakat_maal(bersih, harga_emas, haul):
    nisab = 85 * harga_emas
    if bersih < nisab:
        return nisab, False, "Belum mencapai nisab", 0
    if not haul:
        return nisab, False, "Belum genap haul (1 tahun)", 0
    return nisab, True, "", round(bersih * 0.025)

def rekap_laporan_bulanan(data, bulan):
    per_jenis = {}
    admin = 0
    donatur = 0
    for d in data["donasi"]:
        if d["tanggal"][:7] == bulan and d["status"] == "berhasil":
            jenis = [p["jenis"] for p in data["program"] if p["id"] == d["program"]][0]
            per_jenis[jenis] = per_jenis.get(jenis, 0) + d["jumlah"]
            admin += d["biaya_admin"]
            donatur += 1
    return per_jenis, admin, donatur