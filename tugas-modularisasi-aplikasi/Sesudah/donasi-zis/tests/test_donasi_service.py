import unittest
import datetime
from services.donasi_service import (
    hitung_progres_program,
    cari_program,
    hitung_biaya_admin,
    buat_entri_donasi,
    ambil_donatur_program
)

class TestDonasiService(unittest.TestCase):

    def setUp(self):
        # Data dummy untuk pengujian
        self.mock_data = {
            "program": [
                {"id": "PG001", "nama": "Bantu Sekolah", "target": 1000000},
                {"id": "PG002", "nama": "Bantu Panti", "target": 500000}
            ],
            "donasi": [
                {
                    "id": "DN0001",
                    "program": "PG001",
                    "nama": "Azis",
                    "anonim": False,
                    "jumlah": 500000,
                    "biaya_admin": 3500,
                    "diterima": 496500,
                    "tanggal": "2026-03-01",
                    "status": "berhasil"
                },
                {
                    "id": "DN0002",
                    "program": "PG001",
                    "nama": "Budi",
                    "anonim": True,
                    "jumlah": 600000,
                    "biaya_admin": 0,
                    "diterima": 600000,
                    "tanggal": "2026-03-02",
                    "status": "berhasil"
                }
            ]
        }

    def test_hitung_progres_program(self):
        hasil = hitung_progres_program(self.mock_data)
        # PG001 total diterima 496500 + 600000 = 1096500 (target 1000000 -> 109.6% -> tercapai)
        self.assertEqual(hasil[0]["terkumpul"], 1096500)
        self.assertEqual(hasil[0]["persen"], 109.7)
        self.assertTrue(hasil[0]["tercapai"])

    def test_cari_program(self):
        program = cari_program(self.mock_data, "PG001")
        self.assertIsNotNone(program)
        self.assertEqual(program["nama"], "Bantu Sekolah")

        program_tidak_ada = cari_program(self.mock_data, "PG999")
        self.assertIsNone(program_tidak_ada)

    def test_hitung_biaya_admin(self):
        # Biaya admin QRIS (0.7%)
        self.assertEqual(hitung_biaya_admin("qris", 100000), 700)
        # Biaya admin VA (flat 4000)
        self.assertEqual(hitung_biaya_admin("va", 100000), 4000)
        # Transfer bank (0)
        self.assertEqual(hitung_biaya_admin("transfer", 100000), 0)
        # Metode tidak valid
        self.assertIsNone(hitung_biaya_admin("e-wallet", 100000))

    def test_buat_entri_donasi(self):
        tgl_test = datetime.date(2026, 3, 15)
        entri = buat_entri_donasi(
            nomor=3,
            id_program="PG001",
            nama="Azis",
            anonim=False,
            jumlah=100000,
            metode="va",
            admin=4000,
            tgl=tgl_test
        )
        self.assertEqual(entri["id"], "DN0003")
        self.assertEqual(entri["kuitansi"], "ZIS/2026/03/0003")
        self.assertEqual(entri["diterima"], 96000)
        self.assertEqual(entri["status"], "berhasil")

    def test_ambil_donatur_program(self):
        donatur = ambil_donatur_program(self.mock_data, "PG001")
        self.assertEqual(len(donatur), 2)
        # Pengecekan nama jika anonim == True
        self.assertEqual(donatur[0]["nama"], "Hamba Allah")  # donasi terakhir (reversed)
        self.assertEqual(donatur[1]["nama"], "Azis")

if __name__ == '__main__':
    unittest.main()