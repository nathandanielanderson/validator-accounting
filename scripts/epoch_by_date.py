import requests
from datetime import datetime, timedelta

# Solana RPC Endpoint
RPC_URL = "https://api.mainnet-beta.solana.com"

# Constants
GENESIS_TIMESTAMP = 1596062400  # Solana Genesis (UTC: 2020-07-16 00:00:00)
SLOT_DURATION = 0.4  # Approximate slot duration in seconds

# RPC call to fetch block time for a given slot
def get_block_time(slot):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlockTime",
        "params": [slot]
    }
    response = requests.post(RPC_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error fetching block time: {response.status_code}")
    return response.json().get("result", None)

# Estimate slot from a given timestamp
def estimate_slot_from_timestamp(target_timestamp):
    # Initial estimate
    estimated_slot = int((target_timestamp - GENESIS_TIMESTAMP) / SLOT_DURATION)
    return estimated_slot

# Refine the slot to find the closest match
def find_slot_for_timestamp(target_timestamp, tolerance=10):
    # Estimate the initial slot
    estimated_slot = estimate_slot_from_timestamp(target_timestamp)
    print(f"Initial estimated slot: {estimated_slot}")

    # Refine the slot
    while True:
        block_time = get_block_time(estimated_slot)
        if block_time is None:
            print(f"Slot {estimated_slot} not found, adjusting...")
            estimated_slot -= 1000  # Step backward if the slot is unavailable
            continue

        # Compare the block time with the target timestamp
        time_diff = target_timestamp - block_time
        if abs(time_diff) <= tolerance:
            return estimated_slot

        # Adjust the slot based on the time difference
        if time_diff > 0:
            estimated_slot += int(time_diff / SLOT_DURATION)  # Move forward
        else:
            estimated_slot -= int(abs(time_diff) / SLOT_DURATION)  # Move backward

# Main Function
def main():
    # Input: Date and time in CST
    input_date = "2024/11/20 20:30:00"
    cst_offset = timedelta(hours=-6)  # CST is UTC-6
    input_datetime = datetime.strptime(input_date, "%Y/%m/%d %H:%M:%S") - cst_offset
    target_timestamp = int(input_datetime.timestamp())

    # Find the slot for the given timestamp
    print(f"Finding slot for timestamp: {target_timestamp} ({input_date} CST)")
    slot = find_slot_for_timestamp(target_timestamp)
    print(f"The slot for {input_date} CST is: {slot}")

if __name__ == "__main__":
    main()