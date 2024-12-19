import requests
import csv

# Solana RPC endpoint
RPC_URL = "https://mainnet.helius-rpc.com/?api-key=a2aa86f7-26ec-4b6d-89ae-99b9183ffc4d"

# Stake account addresses
STAKE_ACCOUNTS = [
    "nateBZg7oHVPLB2samBLkKvfzedU3ALZBexMFPMKjn1"  # Replace with your stake account
]

# Get current epoch
def get_current_epoch():
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getEpochInfo"}
    response = requests.post(RPC_URL, json=payload)
    return response.json()["result"]["epoch"]

# Fetch inflation rewards for a given epoch
def fetch_inflation_rewards(epoch):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getInflationReward",
        "params": [STAKE_ACCOUNTS, {"epoch": epoch}]
    }
    response = requests.post(RPC_URL, json=payload)
    return response.json().get("result", [])

# Write results to CSV
def write_to_csv(data):
    with open("commission_rewards.csv", "w", newline="") as csvfile:
        fieldnames = ["Epoch", "Commission Rewards (SOL)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print("✅ Commission Rewards saved to 'commission_rewards.csv'.")

# Main function
def main():
    print("🚀 Starting Commission Reward Calculation...")

    # Get current epoch
    current_epoch = get_current_epoch()
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
        rewards = fetch_inflation_rewards(epoch)
        if not rewards:
            print(f"⚠️ No rewards found for epoch {epoch}. Skipping.")
            continue

        # Commission Rewards
        commission_rewards = rewards[0]["amount"] / 1e9  # Convert lamports to SOL

        # Append data
        all_data.append({
            "Epoch": epoch,
            "Commission Rewards (SOL)": round(commission_rewards, 2)
        })

        print(f"  ✅ Commission Rewards: {commission_rewards:.2f} SOL")

    # Write results to CSV
    write_to_csv(all_data)
    print("🎉 Done!")

if __name__ == "__main__":
    main()