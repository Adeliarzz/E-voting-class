# E-Voting Blockchain System

Sistem e-voting berbasis Blockchain Ethereum menggunakan Truffle, Ganache, dan Web3.js. 
Tujuan project ini adalah membuat proses pemilihan yang aman, transparan, dan tidak dapat dimanipulasi.

---

## 🧩 Teknologi yang Digunakan
- Solidity (Smart Contract)
- Truffle 
- Ganache (Local Blockchain)
- Node.js
- Web3.js
- HTML / CSS / JavaScript (Frontend)

---

## 📂 Struktur Folder
evoting-class/
│
├── contracts/
│ └── ClassVote.sol # Smart contract utama
│
├── migrations/
│ └── 2_deploy_contracts.js
│
├── build/
│ └── contracts/ClassVote.json
│
├── frontend/
│ ├── index.html
│ ├── app.js
│ └── styles.css
│
├── test/
│
├── truffle-config.js
├── read_votes.py
├── package.json
└── hasil_voting.xlsx

## 🚀 Cara Menjalankan Project

### 1️⃣ Jalankan Ganache
- Buka Ganache → New Workspace → Tambahkan truffle-config.js → Start Mining.

### 2️⃣ Compile Smart Contract

- truffle compile
### 3️⃣ Deploy ke Ganache

- truffle migrate --reset
### 4️⃣ Jalankan Frontend
Buka file:
frontend/index.html
Pastikan terhubung ke jaringan Ganache.

---

## 🧠 Penjelasan Smart Contract
Smart contract mencatat:
- daftar kandidat
- jumlah suara
- alamat yang sudah voting
- mencegah voting lebih dari 1 kali

