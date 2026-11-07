import unittest
from services.zakat_service import hitung_zakat_penghasilan, hitung_zakat_maal

class TestZakatService(unittest.TestCase):

    def test_hitung_zakat_penghasilan_wajib(self):
        harga_emas = 1000000  # Nisab = round(85 * 1000000 / 12) = 7083333
        total_penghasilan = 10000000
        
        nisab, wajib, zakat = hitung_zakat_penghasilan(total_penghasilan, harga_emas)
        self.assertEqual(nisab, 7083333)
        self.assertTrue(wajib)
        self.assertEqual(zakat, 250000)  # 2.5% dari 10.000.000

    def test_hitung_zakat_penghasilan_tidak_wajib(self):
        harga_emas = 1000000
        total_penghasilan = 5000000  # Di bawah nisab
        
        nisab, wajib, zakat = hitung_zakat_penghasilan(total_penghasilan, harga_emas)
        self.assertFalse(wajib)
        self.assertEqual(zakat, 0)

    def test_hitung_zakat_maal_sukses(self):
        harga_emas = 1000000  # Nisab = 85.000.000
        bersih = 100000000
        haul = True
        
        nisab, wajib, pesan, zakat = hitung_zakat_maal(bersih, harga_emas, haul)
        self.assertTrue(wajib)
        self.assertEqual(pesan, "")
        self.assertEqual(zakat, 2500000)

    def test_hitung_zakat_maal_belum_nisab(self):
        harga_emas = 1000000
        bersih = 50000000
        haul = True
        
        nisab, wajib, pesan, zakat = hitung_zakat_maal(bersih, harga_emas, haul)
        self.assertFalse(wajib)
        self.assertEqual(pesan, "Belum mencapai nisab")
        self.assertEqual(zakat, 0)

    def test_hitung_zakat_maal_belum_haul(self):
        harga_emas = 1000000
        bersih = 100000000
        haul = False  # Belum 1 tahun
        
        nisab, wajib, pesan, zakat = hitung_zakat_maal(bersih, harga_emas, haul)
        self.assertFalse(wajib)
        self.assertEqual(pesan, "Belum genap haul (1 tahun)")
        self.assertEqual(zakat, 0)

if __name__ == '__main__':
    unittest.main()