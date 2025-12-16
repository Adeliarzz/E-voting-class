import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY")

# Path to Truffle Artifact
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_PATH = os.path.join(BASE_DIR, "build", "contracts", "ClassVote.json")

if not os.path.exists(ARTIFACT_PATH):
    raise FileNotFoundError(f"Truffle artifact not found at {ARTIFACT_PATH}. Did you run 'truffle compile'?")

with open(ARTIFACT_PATH, "r") as f:
    artifact = json.load(f)
    CONTRACT_ABI = artifact["abi"]
    
    # Auto-detect network ID (assuming Ganache 5777 or the first one available)
    networks = artifact["networks"]
    if "5777" in networks:
        CONTRACT_ADDRESS = networks["5777"]["address"]
    else:
        # Fallback: try to grab the last deployed network
        network_ids = list(networks.keys())
        if network_ids:
            latest_id = network_ids[-1]
            CONTRACT_ADDRESS = networks[latest_id]["address"]
        else:
            # Fallback to .env if not found in artifact
            CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

if not CONTRACT_ADDRESS:
    raise ValueError("Contract Address not found in Truffle artifact or .env")

print(f"Loaded Contract at: {CONTRACT_ADDRESS}")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def get_candidates():
    if not w3.is_connected():
        return []
    
    try:
        count = contract.functions.candidatesCount().call()
        candidates = []
        for i in range(1, count + 1):
            c = contract.functions.candidates(i).call()
            # c is [id, name, voteCount]
            candidates.append({
                "id": c[0],
                "name": c[1],
                "voteCount": c[2]
            })
        return candidates
    except Exception as e:
        print(f"Error fetching candidates: {e}")
        return []

def vote_on_blockchain(candidate_id, user_id):
    if not ADMIN_PRIVATE_KEY or "YOUR_ADMIN_PRIVATE_KEY" in ADMIN_PRIVATE_KEY:
        raise Exception("Server Admin Private Key not configured")

    account = w3.eth.account.from_key(ADMIN_PRIVATE_KEY)
    nonce = w3.eth.get_transaction_count(account.address)

    # Build transaction
    tx = contract.functions.vote(candidate_id, user_id).build_transaction({
        'chainId': 5777, # Default Ganache ID, might need adjustment if dynamic
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': nonce,
    })

    # Sign transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=ADMIN_PRIVATE_KEY)

    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt
