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