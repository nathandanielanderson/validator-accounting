import requests
import json

# Load configuration
def load_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

# Fetch inflation rewards for a given epoch
def fetch_inflation_rewards(rpc_url, stake_accounts, epoch):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getInflationReward",
        "params": [stake_accounts, {"epoch": epoch}]
    }
    response = requests.post(rpc_url, json=payload)
    return response.json().get("result", [])

# Write results to JSON
def write_to_json(data):
    with open("./output/commission_rewards.json", "w") as jsonfile:
        json.dump(data, jsonfile, indent=4)
    print("✅ Commission Rewards saved to './output/commission_rewards.json'.")

# Main function
def main():
    print("🚀 Starting Commission Reward Calculation...")

    # Load configuration
    config = load_config()
    rpc_url = config["RPC_URL"]
    stake_accounts = config["STAKE_ACCOUNTS"]

    # Get current epoch
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getEpochInfo"}
    response = requests.post(rpc_url, json=payload)
    current_epoch = response.json()["result"]["epoch"]
    print(f"🔍 Current Epoch: {current_epoch}")

    # Ask user for the starting epoch
    start_epoch = int(input("Enter the starting epoch: "))
    if start_epoch >= current_epoch:
        print("⚠️ Starting epoch must be less than the current epoch.")
        return

    all_data = []

    for epoch in range(start_epoch, current_epoch + 1):
        print(f"🔍 Processing Epoch {epoch}...")

        # Fetch inflation rewards
        rewards = fetch_inflation_rewards(rpc_url, stake_accounts, epoch)
        if not rewards:
            print(f"⚠️ No rewards found for epoch {epoch}. Skipping.")
            continue

        # Commission Rewards
        commission_rewards = rewards[0]["amount"] / 1e9  # Convert lamports to SOL

        # Append data
        all_data.append({
            "Epoch": epoch,
            "Commission Rewards (SOL)": round(commission_rewards, 3)
        })

        print(f"  ✅ Commission Rewards: {commission_rewards:.3f} SOL")

    # Write results to JSON
    write_to_json(all_data)
    print("🎉 Done!")

if __name__ == "__main__":
    main()