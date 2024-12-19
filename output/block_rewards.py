import requests
import datetime

# Solana RPC Endpoint
RPC_URL = "https://api.mainnet-beta.solana.com"

# Validator identity
VALIDATOR_IDENTITY = "YOUR_VALIDATOR_IDENTITY"  # Update with your validator public key

# Function to fetch leader schedule for a given epoch
def fetch_leader_schedule(epoch):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getLeaderSchedule",
        "params": [None, {"epoch": epoch}]
    }
    response = requests.post(RPC_URL, json=payload)
    result = response.json()
    return result.get("result", {})

# Function to fetch confirmed blocks for a range of slots
def fetch_confirmed_blocks(start_slot, end_slot):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlocks",
        "params": [start_slot, end_slot]
    }
    response = requests.post(RPC_URL, json=payload)
    result = response.json()
    return result.get("result", [])

# Function to fetch block rewards for a specific slot
def fetch_block_rewards(slot):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [slot, {"encoding": "json", "transactionDetails": "none", "rewards": True}]
    }
    response = requests.post(RPC_URL, json=payload)
    result = response.json()
    return result.get("result", {}).get("rewards", [])

# Main function to calculate block rewards
def calculate_block_rewards(start_epoch, end_epoch):
    print("🚀 Starting Block Rewards Calculation...")
    total_block_rewards = 0

    for epoch in range(start_epoch, end_epoch + 1):
        print(f"🔍 Processing Epoch {epoch}...")
        leader_schedule = fetch_leader_schedule(epoch)

        if not leader_schedule or VALIDATOR_IDENTITY not in leader_schedule:
            print(f"⚠️ No slots assigned to {VALIDATOR_IDENTITY} in Epoch {epoch}.")
            continue

        slots = leader_schedule[VALIDATOR_IDENTITY]
        print(f"✅ Found {len(slots)} slots assigned to validator.")

        # Fetch confirmed blocks in the slots range
        start_slot = slots[0]
        end_slot = slots[-1]
        confirmed_blocks = fetch_confirmed_blocks(start_slot, end_slot)

        # Calculate rewards
        epoch_rewards = 0
        for slot in confirmed_blocks:
            rewards = fetch_block_rewards(slot)
            for reward in rewards:
                if reward["pubkey"] == VALIDATOR_IDENTITY:
                    epoch_rewards += reward["lamports"] / 1e9  # Convert lamports to SOL

        print(f"  ✅ Block Rewards for Epoch {epoch}: {epoch_rewards:.4f} SOL")
        total_block_rewards += epoch_rewards

    print(f"\n🎉 Total Block Rewards: {total_block_rewards:.4f} SOL")

if __name__ == "__main__":
    start_epoch = int(input("Enter the starting epoch: "))
    end_epoch = int(input("Enter the ending epoch: "))
    calculate_block_rewards(start_epoch, end_epoch)