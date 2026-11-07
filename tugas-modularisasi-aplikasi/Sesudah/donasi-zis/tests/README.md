# 🧪 Unit Testing Aplikasi Donasi & ZIS

Dokumentasi ini berisi panduan dan penjelasan mengenai pengujian unit (*unit testing*) pada projek aplikasi Donasi, Zakat, dan Laporan. Pengujian dibuat menggunakan modul bawaan Python `unittest` untuk menguji logika bisnis secara terisolasi tanpa mengubah data asli.

---

## 📂 Struktur Projek (Folder Tree)

```text
donasi-zis/
│
├── services/                     # Modul logika bisnis utama
│   ├── __init__.py
│   ├── storage.py                # Pembacaan dan penyimpanan data JSON
│   ├── donasi_service.py         # Logika transaksi donasi & perhitungan admin
│   ├── zakat_service.py          # Logika kalkulasi nisab & zakat
│   └── laporan_service.py        # Logika rekapitulasi laporan bulanan
│
├── tests/                        # Folder khusus pengujian unit
│   ├── __init__.py
│   ├── README.md                 # Dokumentasi pengujian & flowchart
│   ├── images/                   # Folder penampung screenshot hasil test
│   │   ├── Screenshot 2026-11-07 105652.png
│   │   └── Screenshot 2026-11-07 113044.png
│   ├── test_donasi_service.py    # Pengujian modul donasi
│   ├── test_zakat_service.py     # Pengujian modul zakat
│   └── test_laporan_service.py   # Pengujian modul laporan
│
└── data.json                     # Database lokal (JSON)
```

---

## 🚀 Cara Menjalankan Pengujian

Jalankan perintah berikut di terminal pada direktori `donasi-zis`:

```bash
# Menjalankan pengujian zakat saja
python -m unittest tests.test_zakat_service -v

# Menjalankan pengujian donasi saja
python -m unittest tests.test_donasi_service -v

# Menjalankan pengujian laporan saja
python -m unittest tests.test_laporan_service -v

# Menjalankan seluruh pengujian unit sekaligus
python -m unittest discover -s tests -t . -v
```

---

## 📊 Flowchart Logika Pengujian

### 1. Alur Kerja Siklus Unit Test (Arrange - Act - Assert)
Siklus standar yang digunakan pada setiap fungsi pengujian untuk memverifikasi kebenaran logika:

```mermaid
flowchart TD
    Start([Mulai Eksekusi Test]) --> Arrange["1. Arrange (Persiapan)<br>Siapkan data dummy / input pengujian"]
    Arrange --> Act["2. Act (Eksekusi)<br>Panggil fungsi service yang diuji"]
    Act --> Assert{"3. Assert (Pemeriksaan)<br>Apakah Hasil Aktual == Nilai Ekspektasi?"}
    
    Assert -- Ya --> Pass["Status: OK (Test Lulus)"]
    Assert -- Tidak --> Fail["Status: FAIL (AssertionError)"]
    
    Pass --> End([Selesai])
    Fail --> End
```

---

### 2. Logika Modul Zakat (`test_zakat_service.py`)

#### A. Zakat Penghasilan (`hitung_zakat_penghasilan`)
```mermaid
flowchart TD
    Start([Mulai: hitung_zakat_penghasilan]) --> Input[Input: total_penghasilan, harga_emas]
    Input --> Calc["Hitung Nisab = round(85 * harga_emas / 12)"]
    Calc --> Check{"total_penghasilan >= nisab?"}
    
    Check -- Ya (Wajib) --> Wajib["wajib = True<br>zakat = round(total * 0.025)"]
    Check -- Tidak --> TidakWajib["wajib = False<br>zakat = 0"]
    
    Wajib --> Ret["Return (nisab, wajib, zakat)"]
    TidakWajib --> Ret
    Ret --> End([Selesai])
```

#### B. Zakat Maal (`hitung_zakat_maal`)
```mermaid
flowchart TD
    Start([Mulai: hitung_zakat_maal]) --> Input[Input: harta_bersih, harga_emas, haul]
    Input --> CalcNisab["Hitung Nisab = 85 * harga_emas"]
    CalcNisab --> CheckNisab{"harta_bersih < nisab?"}
    
    CheckNisab -- Ya --> BelumNisab["Return (nisab, False, 'Belum mencapai nisab', 0)"]
    CheckNisab -- Tidak --> CheckHaul{"Sudah 1 tahun (haul == True)?"}
    
    CheckHaul -- Tidak --> BelumHaul["Return (nisab, False, 'Belum genap haul (1 tahun)', 0)"]
    CheckHaul -- Ya --> WajibMaal["zakat = round(harta_bersih * 0.025)<br>Return (nisab, True, '', zakat)"]
    
    BelumNisab --> End([Selesai])
    BelumHaul --> End
    WajibMaal --> End
```

---

### 3. Logika Modul Donasi (`test_donasi_service.py`)

#### A. Perhitungan Biaya Admin (`hitung_biaya_admin`)
```mermaid
flowchart TD
    Start([Mulai: hitung_biaya_admin]) --> Input[Input: metode, jumlah]
    Input --> Check{"Cek Metode Pembayaran"}
    
    Check -- "qris" --> QRIS["Admin = round(jumlah * 0.007)"]
    Check -- "va" --> VA["Admin = 4000 (flat)"]
    Check -- "transfer" --> Transfer["Admin = 0"]
    Check -- Lainnya --> Invalid["Return None (Metode Tidak Dikenal)"]
    
    QRIS --> End([Return Nilai Admin])
    VA --> End
    Transfer --> End
    Invalid --> End
```

#### B. Filter dan Penyamaran Donatur Anonim (`ambil_donatur_program`)
```mermaid
flowchart TD
    Start([Mulai: ambil_donatur_program]) --> Loop["Iterasi data donasi (urutan reversed)"]
    Loop --> Filter{"program == id_program<br>DAN status == 'berhasil'?"}
    
    Filter -- Ya --> CheckAnonim{"Apakah anonim == True?"}
    Filter -- Tidak --> Next["Lanjut ke data berikutnya"]
    
    CheckAnonim -- Ya --> SetAnonim["nama = 'Hamba Allah'"]
    CheckAnonim -- Tidak --> SetAsli["nama = nama asli donatur"]
    
    SetAnonim --> Append["Tambahkan ke list hasil"]
    SetAsli --> Append
    Append --> Next
    Next --> Done{"Semua data selesai?"}
    Done -- Belum --> Loop
    Done -- Sudah --> End([Return List Donatur])
```

---

### 4. Logika Modul Laporan (`test_laporan_service.py`)

#### Rekapitulasi Laporan Bulanan (`rekap_laporan_bulanan`)
```mermaid
flowchart TD
    Start([Mulai: rekap_laporan_bulanan]) --> Input["Input: data, bulan (contoh: '2026-03')"]
    Input --> Init["Inisialisasi:<br>per_jenis = {}, admin = 0, donatur = 0"]
    Init --> Loop["Iterasi setiap donasi (d)"]
    
    Loop --> Check{"tanggal[:7] == bulan<br>DAN status == 'berhasil'?"}
    
    Check -- Ya --> Accumulate["1. Ambil jenis program<br>2. per_jenis[jenis] += jumlah<br>3. admin += biaya_admin<br>4. donatur += 1"]
    Check -- Tidak --> Next["Abaikan donasi (beda bulan / status gagal)"]
    
    Accumulate --> CheckDone{"Semua donasi selesai diproses?"}
    Next --> CheckDone
    CheckDone -- Belum --> Loop
    CheckDone -- Sudah --> End([Return per_jenis, admin, donatur])
```

---

## 📷 Hasil Eksekusi Unit Test

### 1. Hasil Pengujian Sukses (Semua Test Lulus / OK)
![Hasil Unit Test Sukses](images/Screenshot%202026-11-07%20105652.png)

### 2. Hasil Simulasi Pengujian Gagal (Assertion Error)
![Hasil Unit Test Gagal](images/Screenshot%202026-11-07%20113044.png)
