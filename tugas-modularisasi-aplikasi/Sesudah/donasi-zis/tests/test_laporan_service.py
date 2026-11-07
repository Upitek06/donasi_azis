import unittest
from services.laporan_service import rekap_laporan_bulanan

class TestLaporanService(unittest.TestCase):

    def setUp(self):
        self.mock_data = {
            "program": [
                {"id": "PG001", "jenis": "Pendidikan"},
                {"id": "PG002", "jenis": "Kesehatan"}
            ],
            "donasi": [
                {
                    "program": "PG001",
                    "jumlah": 100000,
                    "biaya_admin": 700,
                    "tanggal": "2026-03-10T10:00:00",
                    "status": "berhasil"
                },
                {
                    "program": "PG001",
                    "jumlah": 200000,
                    "biaya_admin": 0,
                    "tanggal": "2026-03-12T11:00:00",
                    "status": "berhasil"
                },
                {
                    "program": "PG002",
                    "jumlah": 150000,
                    "biaya_admin": 4000,
                    "tanggal": "2026-03-15T09:00:00",
                    "status": "berhasil"
                },
                {
                    "program": "PG001",
                    "jumlah": 500000,
                    "biaya_admin": 0,
                    "tanggal": "2026-02-20T10:00:00",  # Beda bulan (Februari)
                    "status": "berhasil"
                },
                {
                    "program": "PG001",
                    "jumlah": 50000,
                    "biaya_admin": 0,
                    "tanggal": "2026-03-18T10:00:00",
                    "status": "gagal"  # Status bukan berhasil
                }
            ]
        }

    def test_rekap_laporan_bulanan(self):
        per_jenis, admin, donatur = rekap_laporan_bulanan(self.mock_data, "2026-03")
        
        # Pengecekan per jenis program
        self.assertEqual(per_jenis["Pendidikan"], 300000)  # 100000 + 200000
        self.assertEqual(per_jenis["Kesehatan"], 150000)
        
        # Pengecekan total biaya admin (700 + 4000)
        self.assertEqual(admin, 4700)
        
        # Pengecekan total donatur (hanya status berhasil di bulan 2026-03)
        self.assertEqual(donatur, 3)

if __name__ == '__main__':
    unittest.main()