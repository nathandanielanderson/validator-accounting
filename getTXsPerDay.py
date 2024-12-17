import requests
import datetime
import csv
import json
import sys
import os

# Load RPC_URL and Wallet Address from JSON
def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]

# Save the latest seed signature to a file
def save_seed_signature(signature, file_path="seed_signature.txt"):
    with open(file_path, "w") as file:
        file.write(signature)
    print(f"Seed signature saved: {signature}")

# Fetch transactions and write to CSV
def fetch_transactions(wallet_address, rpc_url, start_signature=None):
    headers = {"Content-Type": "application/json"}
    before_signature = start_signature
    transactions_fetched = 0
    earliest_transaction = None

    while True:
        # Prepare the request
        params = {"limit": 500}
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

        # Infer the current day and open a CSV for writing
        for tx in result:
            block_time = tx.get("blockTime", 0)
            signature = tx.get("signature", "N/A")
            readable_time = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')
            current_day = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d')

            # Open CSV file dynamically per day
            if not earliest_transaction:
                output_file = f"{current_day}_{wallet_address}_TXs.csv"
                print(f"Writing to file: {output_file}")
                csvfile = open(output_file, mode="w", newline="")
                writer = csv.DictWriter(csvfile, fieldnames=["Block Time (UTC)", "Signature"])
                writer.writeheader()

            # Write to CSV
            writer.writerow({"Block Time (UTC)": readable_time, "Signature": signature})
            transactions_fetched += 1
            earliest_transaction = signature

        # Update the before_signature for the next batch
        before_signature = result[-1]["signature"]

    if earliest_transaction:
        save_seed_signature(earliest_transaction)
    print(f"Finished fetching {transactions_fetched} transactions.")

# Main
if __name__ == "__main__":
    RPC_URL, WALLET_ADDRESS = load_config()

    # Read the starting transaction signature from CLI or fallback to saved file
    start_signature = None
    if len(sys.argv) > 1:
        start_signature = sys.argv[1]
    elif os.path.exists("seed_signature.txt"):
        with open("seed_signature.txt", "r") as file:
            start_signature = file.read().strip()

    print(f"Starting fetch from signature: {start_signature or 'latest transactions'}")
    fetch_transactions(WALLET_ADDRESS, RPC_URL, start_signature)