import requests
import json
import time
from datetime import datetime

# Load configuration
def load_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

# Fetch transaction signatures in a batch
def fetch_transaction_signatures_batch(rpc_url, identity_account, before=None, limit=100):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            identity_account,
            {"before": before, "limit": limit}
        ]
    }
    response = requests.post(rpc_url, json=payload)
    if response.status_code != 200:
        print(f"⚠️ Error fetching transaction signatures: {response.status_code}")
        return None

    return response.json().get("result", [])

# Fetch transaction details for a given signature
def fetch_transaction_details(rpc_url, signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed"}]
    }
    response = requests.post(rpc_url, json=payload)
    if response.status_code != 200:
        print(f"⚠️ Error fetching transaction details: {response.status_code}")
        return None
    return response.json().get("result", {})

# Process transactions to filter by the specific SOL amount
def process_transactions(rpc_url, identity_account, target_epoch, batch_size=100):
    specific_amount = -0.00206016  # Fixed amount to filter
    before = None
    filtered_signatures = []
    total_processed = 0  # Tally for transactions processed

    while True:
        print(f"🔍 Fetching batch of {batch_size} transactions...")
        batch = fetch_transaction_signatures_batch(rpc_url, identity_account, before, batch_size)
        if not batch:
            print("✅ No more transactions to process.")
            break

        for txn in batch:
            signature = txn["signature"]
            block_time = txn.get("blockTime", 0)
            txn_epoch = block_time // 432000  # Convert block time to epoch

            # Stop if we've reached transactions older than the target epoch
            if txn_epoch < target_epoch:
                print(f"\n✅ Stopped at epoch {txn_epoch}, before target epoch {target_epoch}.")
                return filtered_signatures

            # Fetch transaction details
            transaction_details = fetch_transaction_details(rpc_url, signature)
            if not transaction_details:
                continue

            # Check for the specific SOL amount in the instructions
            meta = transaction_details.get("meta", {})
            pre_balances = meta.get("preBalances", [])
            post_balances = meta.get("postBalances", [])
            if len(pre_balances) > 1 and len(post_balances) > 1:
                balance_diff = (pre_balances[0] - post_balances[0]) / 1e9  # Convert lamports to SOL
                if abs(balance_diff - specific_amount) < 1e-6:  # Match the fixed amount
                    filtered_signatures.append(signature)

            # Increment the running tally
            total_processed += 1

            # Print a static running tally
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\rTransactions Processed: {total_processed} | Current Epoch: {txn_epoch} | Timestamp: {current_time}", end="")

        # Set the `before` parameter to the last signature in the batch for pagination
        before = batch[-1]["signature"]

        # Add a delay to avoid throttling
        time.sleep(1)  # Adjust as needed

    print()  # Ensure the next print starts on a new line
    return filtered_signatures

# Write results to JSON
def write_to_json(data, filename):
    with open(filename, "w") as jsonfile:
        json.dump(data, jsonfile, indent=4)
    print(f"✅ Data saved to '{filename}'.")

# Main function
def main():
    print("🚀 Starting MEV Reward Transaction Filter...")

    # Load configuration
    config = load_config()
    rpc_url = config["RPC_URL"]
    identity_account = config["IDENTITY_ACCOUNT"]

    # Get the target epoch from the user
    target_epoch = int(input("Enter the target epoch to stop processing: "))

    # Process transactions
    filtered_signatures = process_transactions(
        rpc_url, identity_account, target_epoch, batch_size=100
    )
    print(f"\n✅ Found {len(filtered_signatures)} CREATE ACCOUNT transactions with the specific amount.")

    # Save filtered transaction signatures to a JSON file
    write_to_json(filtered_signatures, "./output/filtered_signatures.json")
    print("🎉 Done!")

if __name__ == "__main__":
    main()