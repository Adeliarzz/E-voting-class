# 🗳️ E-Voting Blockchain System

![Python & Flask](https://img.shields.io/badge/Python-Flask-blue?style=for-the-badge&logo=flask)
![Solidity](https://img.shields.io/badge/Smart%20Contract-Solidity-363636?style=for-the-badge&logo=solidity)
![Ganache](https://img.shields.io/badge/Blockchain-Ganache-e4a663?style=for-the-badge)
![Web3.py](https://img.shields.io/badge/Web3-Web3.py-orange?style=for-the-badge)

Sistem E-Voting Aman & Transparan berbasis Blockchain Ethereum. Dibuat untuk demonstrasi pemilihan umum yang tidak dapat dimanipulasi, transparan, dan dapat diaudit secara real-time.

---

## ✨ Fitur Utama

### 🖥️ Halaman Publik (Voter)
- **Landing Page Modern**: Desain Glassmorphism dengan animasi halus dan responsif.
- **Real-Time Clock**: Penunjuk waktu server yang presisi (Jam:Menit:Detik:Milidetik).
- **Kandidat Profile**: Kartu kandidat dengan foto Ketua & Wakil, Visi/Misi (Modal).
- **Proses Voting Aman**:
  - Konfirmasi pilihan dengan SweetAlert.
  - Tanda terima digital (Transaction Hash) setelah memilih.
  - Pencegahan Double Voting (Satu NIK = Satu Suara).
- **Transparency Portal (`/ledger`)**: Block Explorer mini untuk memantau setiap transaksi voting yang masuk ke dalam blok.
- **Live Results (`/results`)**: Grafik donat real-time dan statistik perolehan suara.

### 🛡️ Panel Admin
- **Dashboard Statistik**: Total User, Total Suara, Status Koneksi Blockchain.
- **Manajemen Kandidat**: Tambah/Hapus kandidat dengan upload foto.
- **Manajemen User**:
  - **Daftar User**: Melihat user terdaftar.
  - **Hapus User**: Menghapus user yang tidak valid.
  - **Privacy**: Private Key user tidak ditampilkan demi keamanan.
- **Status Koneksi**: Indikator real-time koneksi ke Ganache.

---

## 🛠️ Persyaratan Sistem

Pastikan PC Anda sudah terinstall:
1.  **Python 3.8+** (Untuk menjalankan server Flask).
2.  **Node.js & NPM** (Untuk Truffle).
3.  **Ganache GUI** (Untuk simulasi Blockchain lokal).

---

## 🚀 Cara Instalasi & Menjalankan

Ikuti langkah-langkah ini agar teman Anda bisa menjalankannya dengan mudah:

### 1. Persiapkan Ganache
1. Buka aplikasi **Ganache**.
2. Klik **"New Workspace"**.
3. Beri nama workspace (bebas).
4. Klik tab **"Server"**, pastikan Port Number adalah **7545**.
5. Klik **"Save Workspace"**.

### 2. Instalasi Dependensi
Buka terminal di dalam folder project ini:

```bash
# 1. Install Library Python
pip install -r requirements.txt

# 2. Install Truffle secara Global (jika belum ada)
npm install -g truffle
```

> **Note**: Jika tidak ada file `requirements.txt`, install manual:
> `pip install flask flask-sqlalchemy web3 python-dotenv`

### 3. Konfigurasi Environment (.env) ⚠️ PENTING
Aplikasi membutuhkan Private Key Admin agar bisa berinteraksi dengan Blockchain.

1. Buat file baru bernama `.env` (jika belum ada).
2. Buka **Ganache**, lihat akun paling atas (Index 0).
3. Klik icon **Kunci 🔑** di sebelah kanan akun tersebut.
4. Salin **Private Key**.
5. Isi file `.env` seperti ini:

```env
RPC_URL=http://127.0.0.1:7545
ADMIN_PRIVATE_KEY=0x...(paste private key dari Ganache disini)
```

### 4. Deploy Smart Contract
Agar aplikasi mengenali Blockchain Anda, kita perlu "meng-upload" kontrak ke Ganache:

```bash
truffle migrate --reset
```

### 5. Jalankan Aplikasi
Sekarang jalankan server Python-nya:

```bash
python app.py
```

Buka browser dan akses:
👉 **http://127.0.0.1:5000**

---

## 📂 Struktur Folder Utama

```
evoting-class/
├── app.py                # File Utama Server (Python Flask)
├── contracts/            # Kode Smart Contract (Solidity)
│   └── Evoting.sol
├── templates/            # Halaman Frontend (HTML)
│   ├── index.html        # Landing Page
│   ├── admin_layout.html # Layout Admin
│   └── ledger.html       # Block Explorer
├── static/               # CSS, Gambar, Uploads
├── migrations/           # Skrip Deploy Truffle
└── requirements.txt      # Daftar Library Python
```

---

## ⚠️ Troubleshooting (Masalah Umum)

**Q: Error "Insufficient Funds" saat deploy?**
A: Ganache mungkin perlu di-restart. Restart Ganache, lalu update `.env` dengan Private Key baru, dan jalankan `truffle migrate --reset` lagi.

**Q: Error "Contract Logic Error" di `/results`?**
A: Artinya kontrak belum di-deploy ke sesi Ganache yang aktif. Matikan server, jalankan `truffle migrate --reset`, lalu nyalakan server lagi.

**Q: Gambar kandidat tidak muncul?**
A: Pastikan folder `static/uploads` ada. Saat menambah kandidat baru, gambar akan tersimpan di sana.

---

> Dibuat dengan ❤️ untuk Pembelajaran Blockchain.
