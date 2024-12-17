import requests
import datetime
import json

# Load RPC_URL and Wallet Address from JSON
def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]

# Fetch transactions until reaching the target day
def fetch_transactions_until_date(wallet_address, rpc_url, target_date):
    headers = {"Content-Type": "application/json"}
    before_signature = None  # For pagination
    transactions_fetched = 0

    # Convert target_date to timestamp (CST → UTC)
    target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
    target_timestamp = int(target_date_obj.timestamp())
    

    print(f"Fetching transactions starting from the most recent until {target_date}...")

    while True:
        # Set up the request payload
        params = {"limit": 1000}  # Fetch 100 transactions per request
        if before_signature:
            params["before"] = before_signature

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet_address, params]
        }

        response = requests.post(rpc_url, json=payload, headers=headers).json()
        result = response.get("result", [])

        if not result:
            print("\nNo more transactions found.")
            break

        for tx in result:
            block_time = tx.get("blockTime", 0)
            signature = tx.get("signature", "N/A")
            readable_time = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')

            # Check if we've reached the target date
            if block_time < target_timestamp:
                print(f"\nReached transactions older than {target_date}. Stopping.")
                return transactions_fetched

            # Process the transaction
            transactions_fetched += 1
            print(f"\nTransaction {transactions_fetched}:")
            print(f"  Signature: {signature}")
            print(f"  Block Time (UTC): {readable_time}")

        # Prepare for the next batch
        before_signature = result[-1]["signature"]

    print(f"\nFinished fetching {transactions_fetched} transactions.")
    
    return transactions_fetched

# Main
if __name__ == "__main__":
    # Load configuration
    RPC_URL, WALLET_ADDRESS = load_config()

    # Target date: Stop fetching when transactions are older than this date
    TARGET_DATE = "2024-12-17"

    # Fetch transactions
    fetch_transactions_until_date(WALLET_ADDRESS, RPC_URL, TARGET_DATE)