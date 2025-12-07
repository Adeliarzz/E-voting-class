import json
from web3 import Web3
import pandas as pd

# CONNECT KE GANACHE GUI
ganache_url = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))

print("Connected:", w3.is_connected())

# LOAD ABI DARI ARTIFACT TRUFFLE
with open("build/contracts/ClassVote.json") as f:
    artifact = json.load(f)

abi = artifact["abi"]

# GANTI DENGAN ALAMAT KONTRAKMU
contract_address = "0x44beA6f33C18b3E70E20529e8b547c03f3C0C877"

contract = w3.eth.contract(address=contract_address, abi=abi)

# BACA JUMLAH KANDIDAT
c_count = contract.functions.candidatesCount().call()
print("Total candidates:", c_count)

rows = []

# LOOP AMBIL KANDIDAT
for i in range(1, c_count + 1):
    cid, name, votes = contract.functions.candidates(i).call()
    rows.append({"id": cid, "name": name, "voteCount": votes})

df = pd.DataFrame(rows)
print(df)

# SIMPAN HASIL KE EXCEL
df.to_excel("hasil_voting.xlsx", index=False)
print("Laporan tersimpan sebagai hasil_voting.xlsx")