import requests
import datetime
import csv
import json

# Load RPC_URL and Wallet Address from JSON
def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]

# Function to search for the signature closest to the end-blocktime of the target date
def find_starting_signature(wallet_address, rpc_url, target_date):
    headers = {"Content-Type": "application/json"}
    end_of_day = datetime.datetime.strptime(target_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    end_timestamp = int(end_of_day.timestamp())

    before_signature = None
    print(f"Searching for the starting signature closest to the target date ({target_date} ending at 23:59:59)...\n")

    while True:
        # Fetch a batch of 100 transactions
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
            print("No transactions found for the specified date.")
            return None

        # Check the transactions in reverse (from latest to oldest)
        for tx in result:
            block_time = tx.get("blockTime", 0)
            signature = tx.get("signature", "N/A")
            current_date = datetime.datetime.utcfromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')

            print(f"Checking Signature: {signature} | Current Block Time: {current_date} | Target Date: {target_date} 23:59:59")

            if block_time <= end_timestamp:
                print(f"\nFound starting signature: {signature} at {current_date}")
                return signature

        # Move to the next batch
        before_signature = result[-1]["signature"]
        print(f"Continuing search with batch before signature: {before_signature}...\n")

# Fetch transactions starting from a specific signature and save to CSV
def fetch_and_save_signatures(wallet_address, rpc_url, target_date, starting_signature):
    headers = {"Content-Type": "application/json"}
    before_signature = starting_signature
    transactions_fetched = 0

    # Convert target_date to timestamp
    target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
    target_timestamp = int(target_date_obj.timestamp())

    # Generate output CSV file name
    formatted_date = target_date_obj.strftime("%y-%m-%d")
    output_file = f"{formatted_date}_{wallet_address}_TXs.csv"

    print(f"Fetching transactions until {target_date} and saving to {output_file}...\n")

    # Open the CSV file for writing
    with open(output_file, mode="w", newline="") as csvfile:
        fieldnames = ["Block Time (UTC)", "Signature"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

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

            # Process the transactions
            for tx in result:
                block_time = tx.get("blockTime", 0)
                signature = tx.get("signature", "N/A")
                readable_time = datetime.datetime.utcfromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')

                # Stop when reaching transactions older than the target date
                if block_time < target_timestamp:
                    print(f"Reached transactions older than {target_date}. Stopping.")
                    return

                # Write the timestamp and signature to CSV
                writer.writerow({"Block Time (UTC)": readable_time, "Signature": signature})
                transactions_fetched += 1

                print(f"Transaction {transactions_fetched}: {readable_time} | {signature}")

            # Prepare for the next batch
            before_signature = result[-1]["signature"]

    print(f"\nFinished fetching {transactions_fetched} transactions. Data saved to {output_file}.")

# Main
if __name__ == "__main__":
    RPC_URL, WALLET_ADDRESS = load_config()
    TARGET_DATE = "2024-12-16"  # Replace with the date you want to fetch

    print("Searching for the starting signature closest to the target date...\n")
    starting_signature = find_starting_signature(WALLET_ADDRESS, RPC_URL, TARGET_DATE)

    if starting_signature:
        fetch_and_save_signatures(WALLET_ADDRESS, RPC_URL, TARGET_DATE, starting_signature)
    else:
        print("No starting signature found.")