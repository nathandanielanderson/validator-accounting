import requests
import datetime
import json

# Load RPC_URL and Wallet Address from JSON
def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]

# Fetch all available transactions and record start/end for each day
def get_all_signature_bounds(wallet_address, rpc_url):
    headers = {"Content-Type": "application/json"}
    before_signature = None
    transactions_fetched = 0
    daily_bounds = {}  # Dictionary to store start/end transactions for each date

    print("Fetching all available transactions to record daily bounds...\n")

    while True:
        # Set up the request payload
        params = {"limit": 100}
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
            print("No more transactions found.")
            break

        # Process each transaction
        for tx in result:
            block_time = tx.get("blockTime", 0)
            signature = tx.get("signature", "N/A")

            # Convert block time to human-readable date
            tx_date = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d')

            # If date not already recorded, set start and end for the day
            if tx_date not in daily_bounds:
                daily_bounds[tx_date] = {
                    "start_transaction": {"signature": signature, "block_time": tx_date + " 00:00:00"},
                    "end_transaction": {"signature": signature, "block_time": tx_date + " 23:59:59"},
                }

            # Continuously update the start and end for the day
            daily_bounds[tx_date]["start_transaction"] = {
                "signature": signature,
                "block_time": datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')
            }

            transactions_fetched += 1
            print(f"Transaction {transactions_fetched}: Date: {tx_date} | Signature: {signature}")

        # Prepare for the next batch
        before_signature = result[-1]["signature"]

    return daily_bounds

# Save results to a JSON file
def save_bounds_to_file(wallet_address, daily_bounds):
    output_file = f"all_days_{wallet_address}_Bounds.json"
    with open(output_file, "w") as file:
        json.dump(daily_bounds, file, indent=4)
    print(f"\nDaily bounds saved to {output_file}")

# Main
if __name__ == "__main__":
    RPC_URL, WALLET_ADDRESS = load_config()
    daily_bounds = get_all_signature_bounds(WALLET_ADDRESS, RPC_URL)
    if daily_bounds:
        save_bounds_to_file(WALLET_ADDRESS, daily_bounds)
    else:
        print("No transactions found for the wallet.")