from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if w3.is_connected():
    print(f"--- Ganache Diagnostic ---")
    
    # Check Ganache Account 0
    try:
        acc0 = w3.eth.accounts[0]
        bal0 = w3.from_wei(w3.eth.get_balance(acc0), 'ether')
        print(f"Ganache Account [0]: {acc0}")
        print(f"Balance: {bal0} ETH")
    except Exception as e:
        print(f"Could not fetch Account 0: {e}")

    # Check .env Key
    env_key = os.getenv("ADMIN_PRIVATE_KEY")
    if env_key:
        try:
            env_acc = Account.from_key(env_key)
            env_addr = env_acc.address
            env_bal = w3.from_wei(w3.eth.get_balance(env_addr), 'ether')
            print(f"\n--- .env Configuration ---")
            print(f"ADMIN_PRIVATE_KEY Address: {env_addr}")
            print(f"Balance: {env_bal} ETH")
            
            if acc0.lower() == env_addr.lower():
                print("\n[SUCCESS] .env Key MATCHES Ganache Account 0.")
            else:
                print("\n[WARNING] .env Key DOES NOT MATCH Ganache Account 0.")
                print("ACTION REQUIRED: Update .env with the Private Key of Ganache Account 0.")
        except Exception as e:
            print(f"Invalid Private Key in .env: {e}")
    else:
        print("ADMIN_PRIVATE_KEY missing in .env")

else:
    print("Failed to connect to Ganache.")
