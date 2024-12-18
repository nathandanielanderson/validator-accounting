import requests
import csv
import datetime

# Solana RPC endpoint
RPC_URL = "https://mainnet.helius-rpc.com/?api-key=a2aa86f7-26ec-4b6d-89ae-99b9183ffc4d"

# Stake account addresses (update with your accounts)
STAKE_ACCOUNTS = [
    "nateBZg7oHVPLB2samBLkKvfzedU3ALZBexMFPMKjn1"
]

# Function to fetch current epoch
def get_current_epoch():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getEpochInfo"
    }
    response = requests.post(RPC_URL, json=payload)
    result = response.json()
    return result["result"]["epoch"]-1

# Function to fetch inflation rewards for given epoch
def fetch_inflation_rewards(stake_accounts, epoch):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getInflationReward",
        "params": [stake_accounts, {"epoch": epoch}]
    }
    response = requests.post(RPC_URL, json=payload)
    result = response.json()
    return result.get("result", [])

# Write rewards to a CSV file
def write_rewards_to_csv(rewards_data, filename="inflation_rewards.csv"):
    with open(filename, mode="w", newline="") as csvfile:
        fieldnames = ["Epoch", "Stake Account", "Amount (Lamports)", "Post Balance", "Commission"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for reward in rewards_data:
            writer.writerow({
                "Epoch": reward["epoch"],
                "Stake Account": reward["stake_account"],
                "Amount (Lamports)": reward["amount"],
                "Post Balance": reward["postBalance"],
                "Commission": reward.get("commission", "N/A")
            })
    print(f"✅ Rewards saved to {filename}")

# Main Function
def main():
    print("🚀 Starting Inflation Reward Fetcher...")
    
    # Get current epoch
    current_epoch = get_current_epoch()
    print(f"🔍 Current Epoch: {current_epoch}")
    
    # To store rewards data
    all_rewards = []

    # Iterate backward through epochs
    for epoch in range(current_epoch, 0, -1):  # Start at current epoch, move backward
        print(f"📡 Fetching rewards for epoch {epoch}...")
        rewards = fetch_inflation_rewards(STAKE_ACCOUNTS, epoch)

        # Stop when no rewards are found for any account
        if not any(rewards):
            print(f"⚠️ No rewards found at epoch {epoch}. Stopping.")
            break

        # Parse and store rewards
        for i, reward in enumerate(rewards):
            if reward:
                all_rewards.append({
                    "epoch": epoch,
                    "stake_account": STAKE_ACCOUNTS[i],
                    "amount": reward["amount"],
                    "postBalance": reward["postBalance"],
                    "commission": reward.get("commission", "N/A")
                })
        
        print(f"✅ Fetched rewards for epoch {epoch}")

    # Save to CSV
    if all_rewards:
        write_rewards_to_csv(all_rewards)
    else:
        print("⚠️ No rewards to save. Exiting.")

if __name__ == "__main__":
    main()