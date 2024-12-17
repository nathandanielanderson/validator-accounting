import requests
import datetime
import json

# Load RPC_URL and Wallet Address from JSON
def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]

# Fetch transactions starting from the most recent
def fetch_transactions_iteratively(wallet_address, rpc_url):
    headers = {"Content-Type": "application/json"}
    before_signature = None  # For pagination
    transactions_fetched = 0

    print("Fetching transactions starting from the most recent...")

    while True:
        # Set up the request payload
        params = {"limit": 50}  # Fetch 50 transactions per request
        if before_signature:
            params["before"] = before_signature

        print(f"Fetching batch before signature: {before_signature}")  # Debugging output

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet_address, params]
        }

        # Make the RPC request
        response = requests.post(rpc_url, json=payload, headers=headers).json()
        result = response.get("result", [])

        if not result:
            print("\nNo more transactions found.")
            break

        # Process the transactions
        for tx in result:
            block_time = tx.get("blockTime", 0)
            signature = tx.get("signature", "N/A")
            readable_time = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')

            transactions_fetched += 1
            print(f"\nTransaction {transactions_fetched}:")
            print(f"  Signature: {signature}")
            print(f"  Block Time (UTC): {readable_time}")

        # Prepare for the next batch
        before_signature = result[-1]["signature"]

    print(f"\nFinished fetching {transactions_fetched} transactions.")

# Main
if __name__ == "__main__":
    # Load configuration
    RPC_URL, WALLET_ADDRESS = load_config()

    # Fetch transactions iteratively
    fetch_transactions_iteratively(WALLET_ADDRESS, RPC_URL)