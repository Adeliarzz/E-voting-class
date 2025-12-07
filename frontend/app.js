// app.js (untuk ethers v5 UMD)
// Sesuaikan RPC_URL & CONTRACT_ADDRESS kalau perlu
const RPC_URL = "http://127.0.0.1:7545"; // atau 7545/7545 sesuai Ganache GUI
const CONTRACT_ADDRESS = "0x55D7C11FEF6D3f80297D9247B041FE43d0974a14"; // ganti sesuai hasil migrate

let provider;
let signer;   // ethers.Wallet bila private key diisi
let contract; // ethers.Contract (bisa read-only dengan provider atau connect dengan signer)

// ----------------- ABI (pakai ABI dari ClassVote.json kamu) -----------------
const ABI = [
  {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
  {"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"id","type":"uint256"},{"indexed":false,"internalType":"string","name":"name","type":"string"}],"name":"CandidateAdded","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"voter","type":"address"},{"indexed":false,"internalType":"uint256","name":"candidateId","type":"uint256"}],"name":"Voted","type":"event"},
  {"anonymous":false,"inputs":[],"name":"VotingClosed","type":"event"},
  {"anonymous":false,"inputs":[],"name":"VotingOpened","type":"event"},
  {"inputs":[],"name":"admin","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function","constant":true},
  {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"candidates","outputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"string","name":"name","type":"string"},{"internalType":"uint256","name":"voteCount","type":"uint256"}],"stateMutability":"view","type":"function","constant":true},
  {"inputs":[],"name":"candidatesCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function","constant":true},
  {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"hasVoted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function","constant":true},
  {"inputs":[],"name":"votingOpen","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function","constant":true},
  {"inputs":[{"internalType":"string","name":"_name","type":"string"}],"name":"addCandidate","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"openVoting","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"closeVoting","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"_candidateId","type":"uint256"}],"name":"vote","outputs":[],"stateMutability":"nonpayable","type":"function"}
];
// ---------------------------------------------------------------------------

// elemen UI
const contractAddressEl = document.getElementById("contractAddress");
const errorMsgEl = document.getElementById("errorMsg");
const refreshBtn = document.getElementById("refreshBtn");
const candidatesListEl = document.getElementById("candidatesList");

const pkInput = document.getElementById("pkInput");
const usePkBtn = document.getElementById("usePkBtn");
const clearPkBtn = document.getElementById("clearPkBtn");

const addCandidateBtn = document.getElementById("addCandidateBtn");
const openVotingBtn = document.getElementById("openVotingBtn");
const closeVotingBtn = document.getElementById("closeVotingBtn");
const newCandidateName = document.getElementById("newCandidateName");

const voteBtn = document.getElementById("voteBtn");
const voteIdInput = document.getElementById("voteId");

let adminAddress = null;

// disable admin buttons by default
function setAdminButtons(active) {
  addCandidateBtn.disabled = !active;
  openVotingBtn.disabled = !active;
  closeVotingBtn.disabled = !active;
}

// init: connect provider + read-only contract (ethers v5)
async function init() {
  try {
    // Di ethers v5: provider diakses via ethers.providers
    provider = new ethers.providers.JsonRpcProvider(RPC_URL);

    // contract read-only dengan provider
    contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);

    contractAddressEl.textContent = CONTRACT_ADDRESS;
    errorMsgEl.textContent = "";

    // coba baca admin address (untuk info)
    try {
      adminAddress = await contract.admin();
      console.log("Contract admin:", adminAddress);
    } catch (e) {
      console.warn("Gagal baca admin:", e);
    }

    await refreshCandidates();
  } catch (e) {
    console.error("Init error:", e);
    contractAddressEl.textContent = "(error connecting)";
    errorMsgEl.textContent = "Init error: " + (e.message || e);
    candidatesListEl.textContent = "Contract not connected.";
    setAdminButtons(false);
  }
}

// refresh list kandidat (read-only)
async function refreshCandidates() {
  if (!contract) {
    errorMsgEl.textContent = "Contract not connected.";
    return;
  }
  errorMsgEl.textContent = "";
  candidatesListEl.innerHTML = "Loading...";
  try {
    const countBN = await contract.candidatesCount();
    const count = countBN.toNumber();
    if (count === 0) {
      candidatesListEl.innerHTML = "<i>Belum ada kandidat.</i>";
      return;
    }

    let html = "<ul>";
    for (let i = 1; i <= count; i++) {
      const c = await contract.candidates(i);
      html += `<li><strong>${c.name}</strong> (id: ${c.id.toNumber()}) — votes: ${c.voteCount.toNumber()}</li>`;
    }
    html += "</ul>";
    candidatesListEl.innerHTML = html;
  } catch (e) {
    console.error(e);
    errorMsgEl.textContent = "Error: " + (e.message || e);
    candidatesListEl.textContent = "Contract not connected.";
  }
}

// gunakan private key untuk jadi signer (transact)
async function usePrivateKey() {
  const pk = pkInput.value.trim();
  if (!pk) {
    alert("Masukkan private key Ganache (0x...)");
    return;
  }
  try {
    // ethers v5 Wallet:
    signer = new ethers.Wallet(pk, provider); // Wallet otomatis terhubung ke provider
    contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, signer); // signer-contract

    const signerAddress = await signer.getAddress();
    const contractAdmin = await contract.admin();
    console.log("signer:", signerAddress, "admin:", contractAdmin);
    if (signerAddress.toLowerCase() === contractAdmin.toLowerCase()) {
      setAdminButtons(true);
    } else {
      setAdminButtons(false);
    }
    errorMsgEl.textContent = "Connected as: " + signerAddress;
    contractAddressEl.textContent = CONTRACT_ADDRESS + " (connected)";
    await refreshCandidates();
  } catch (e) {
    console.error("usePk error:", e);
    errorMsgEl.textContent = "Error using private key: " + (e.message || e);
  }
}

function clearPrivateKey() {
  pkInput.value = "";
  signer = null;
  // kembali ke read-only provider contract
  contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);
  setAdminButtons(false);
  errorMsgEl.textContent = "";
}

// TRANSAKSI ADMIN
async function addCandidate() {
  const name = newCandidateName.value.trim();
  if (!name) return alert("Masukkan nama kandidat");
  try {
    const tx = await contract.addCandidate(name);
    errorMsgEl.textContent = "Sending tx... waiting confirmation";
    await tx.wait();
    errorMsgEl.textContent = "Candidate added.";
    newCandidateName.value = "";
    await refreshCandidates();
  } catch (e) {
    console.error(e);
    errorMsgEl.textContent = "Error: " + (e.message || e);
  }
}

async function openVoting() {
  try {
    const tx = await contract.openVoting();
    errorMsgEl.textContent = "Opening voting... wait";
    await tx.wait();
    errorMsgEl.textContent = "Voting opened.";
  } catch (e) {
    console.error(e);
    errorMsgEl.textContent = "Error: " + (e.message || e);
  }
}

async function closeVoting() {
  try {
    const tx = await contract.closeVoting();
    errorMsgEl.textContent = "Closing voting... wait";
    await tx.wait();
    errorMsgEl.textContent = "Voting closed.";
  } catch (e) {
    console.error(e);
    errorMsgEl.textContent = "Error: " + (e.message || e);
  }
}

// VOTE (transaksi)
async function vote() {
  const idStr = voteIdInput.value.trim();
  if (!idStr) return alert("Masukkan ID kandidat");
  const id = Number(idStr);
  if (Number.isNaN(id)) return alert("ID harus angka");
  try {
    const tx = await contract.vote(id);
    errorMsgEl.textContent = "Sending vote... wait";
    await tx.wait();
    errorMsgEl.textContent = "Vote berhasil.";
    await refreshCandidates();
  } catch (e) {
    console.error(e);
    errorMsgEl.textContent = "Error: " + (e.message || e);
  }
}

// listeners
refreshBtn.addEventListener("click", refreshCandidates);
usePkBtn.addEventListener("click", usePrivateKey);
clearPkBtn.addEventListener("click", clearPrivateKey);
addCandidateBtn.addEventListener("click", addCandidate);
openVotingBtn.addEventListener("click", openVoting);
closeVotingBtn.addEventListener("click", closeVoting);
voteBtn.addEventListener("click", vote);

// disable admin by default
setAdminButtons(false);

// init on load
window.addEventListener("load", init);
