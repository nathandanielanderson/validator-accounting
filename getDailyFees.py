import requests
import datetime
import json

# Load RPC_URL and Wallet Address from JSON
def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]

# Fetch a single transaction
def fetch_single_transaction(wallet_address, rpc_url):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet_address,
            {"limit": 1}  # Fetch only 1 transaction
        ]
    }

    response = requests.post(rpc_url, json=payload, headers=headers).json()
    result = response.get("result", [])

    if not result:
        print("No transactions found.")
        return None

    # Extract and display the transaction signature and timestamp
    transaction = result[0]
    block_time = transaction.get("blockTime", 0)
    signature = transaction.get("signature", "N/A")

    # Convert block time to human-readable UTC
    readable_time = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Transaction Signature: {signature}")
    print(f"Block Time (UTC): {readable_time}")
    return transaction

# Main
if __name__ == "__main__":
    # Load configuration
    RPC_URL, WALLET_ADDRESS = load_config()

    print("Fetching a single transaction...")
    fetch_single_transaction(WALLET_ADDRESS, RPC_URL)