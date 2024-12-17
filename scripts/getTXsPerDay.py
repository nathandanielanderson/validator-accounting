import requests
import datetime
import csv
import json
import time
import random

# Load RPC_URL and Wallet Address from JSON
def load_config(file_path="config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]

# Fetch transactions and save to CSV
def fetch_and_save_transactions(wallet_address, rpc_url, starting_signature):
    headers = {"Content-Type": "application/json"}
    before_signature = starting_signature
    transactions_fetched = 0
    retries = 0  # Retry counter for incomplete/empty batches

    # Infer date from the starting signature
    target_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Default fallback
    formatted_date = None

    # Output CSV file
    output_file = None
    print("Starting transaction fetching...\n")

    last_block_time = None  # Initialize last block time for sequential check

    while True:
        try:
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
                retries += 1
                print(f"Empty batch received. Retry {retries}/3...")
                if retries >= 3:
                    print("No more transactions found after retries. Ending.")
                    break
                time.sleep(1)  # Retry delay
                continue

            retries = 0  # Reset retries on valid batch

            # Infer date and open CSV file
            if not formatted_date:
                inferred_date = datetime.datetime.fromtimestamp(result[0]["blockTime"], datetime.UTC).strftime("%Y-%m-%d")
                formatted_date = datetime.datetime.strptime(inferred_date, "%Y-%m-%d").strftime("%y-%m-%d")
                output_file = f"{formatted_date}_{wallet_address}_TXs.csv"

                csvfile = open(output_file, mode="w", newline="")
                fieldnames = ["Block Time (UTC)", "Signature"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

            # Process transactions
            for tx in result:
                block_time = tx.get("blockTime", 0)
                signature = tx.get("signature", "N/A")
                readable_time = datetime.datetime.fromtimestamp(block_time, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')

                # Check for out-of-order transactions (relaxed to allow identical timestamps)
                if last_block_time and block_time > last_block_time:
                    print(f"Warning: Out of order transaction detected but allowing: {readable_time}")
                last_block_time = block_time

                writer.writerow({"Block Time (UTC)": readable_time, "Signature": signature})
                transactions_fetched += 1

                print(f"Transaction {transactions_fetched}: {readable_time} | {signature}")

            before_signature = result[-1]["signature"]
            time.sleep(1 + random.uniform(0.1, 0.5))  # Add small delay to respect limits

        except Exception as e:
            print(f"Error occurred: {e}")
            retries += 1
            if retries >= 3:
                print("Exceeded retries due to errors. Stopping.")
                break
            time.sleep(5)

    if csvfile:
        csvfile.close()
    print(f"\nFinished fetching {transactions_fetched} transactions. Data saved to {output_file}.")
    return before_signature

# Main
if __name__ == "__main__":
    RPC_URL, WALLET_ADDRESS = load_config()
    STARTING_SIGNATURE = "2KHVMv2zPKAZq48D2hceZLoNGj3P4bax8NzQSwLCb1stGa8FYSPxFbTTCiRpyS8j758JaBMRxhAxLWsG8nTZrtn1"  # Replace or pass via CLI

    # Run fetch process
    next_signature = fetch_and_save_transactions(WALLET_ADDRESS, RPC_URL, STARTING_SIGNATURE)
    if next_signature:
        print(f"\nRestart the script with new seed: {next_signature}")
    else:
        print("\nAll transactions fetched successfully.")