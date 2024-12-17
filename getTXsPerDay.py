import requests
import datetime
import csv
import json
import os

# Load configuration (RPC URL and Wallet Address)
def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]

# Fetch transactions from the RPC endpoint
def fetch_transactions(wallet_address, rpc_url, before_signature=None, limit=500):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet_address, {"limit": limit, "before": before_signature}]
    }
    response = requests.post(rpc_url, json=payload, headers=headers).json()
    return response.get("result", [])

# Write a single transaction to its daily CSV file
def write_to_csv(transaction, wallet_address):
    block_time = transaction.get("blockTime", 0)
    signature = transaction.get("signature", "N/A")
    
    # Convert blockTime to date string
    date_str = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d')
    readable_time = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')
    
    # Define file name for the day
    file_name = f"{date_str}_{wallet_address}_TXs.csv"
    
    # Append transaction to the CSV file
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header if the file is new
        if not file_exists:
            writer.writerow(["Block Time (UTC)", "Signature"])
        writer.writerow([readable_time, signature])

# Main function to process all transactions
def process_transactions(wallet_address, rpc_url):
    before_signature = None  # Start at the most recent transaction
    total_transactions = 0

    print("Starting to fetch transactions...")

    while True:
        # Fetch a batch of transactions
        transactions = fetch_transactions(wallet_address, rpc_url, before_signature)
        if not transactions:
            print("No more transactions found. Process complete.")
            break

        # Process each transaction
        for tx in transactions:
            total_transactions += 1
            write_to_csv(tx, wallet_address)

            # Print progress
            block_time = tx.get("blockTime", 0)
            date_str = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d')
            print(f"Processed Transaction {total_transactions}: Date {date_str}, Signature: {tx['signature']}")

        # Set the `before` parameter for the next batch
        before_signature = transactions[-1]["signature"]

    print(f"Finished processing {total_transactions} transactions.")

# Entry point
if __name__ == "__main__":
    RPC_URL, WALLET_ADDRESS = load_config()
    process_transactions(WALLET_ADDRESS, RPC_URL)