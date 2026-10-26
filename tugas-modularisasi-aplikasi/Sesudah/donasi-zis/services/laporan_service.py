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