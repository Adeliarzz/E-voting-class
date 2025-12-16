import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if w3.is_connected():
    print(f"Connected to Ganache. Network ID: {w3.net.version}")
    
    try:
        with open('build/contracts/Evoting.json') as f:
            data = json.load(f)
            networks = data.get('networks', {})
            print(f"Artifact Networks: {list(networks.keys())}")
            
            nid = str(w3.net.version)
            if nid in networks:
                addr = networks[nid]['address']
                print(f"MATCH! Contract Address: {addr}")
                
                # Check if code exists
                code = w3.eth.get_code(addr)
                if len(code) > 2: # '0x' + bytes
                    print("STATUS: Contract Code Found (Active).")
                else:
                    print("STATUS: NO CODE! Contract is missing (Chain Reset?).")
            else:
                print("MISMATCH! Current Network ID not in Artifact.")
    except Exception as e:
        print(f"Error reading artifact: {e}")
else:
    print("Failed to connect to Ganache.")
