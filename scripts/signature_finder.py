import requests
import datetime
from utils import safe_request

def find_starting_signature(wallet_address, rpc_url, target_date):
    """Find the first signature closest to the end-blocktime of a target date."""
    headers = {"Content-Type": "application/json"}
    end_of_day = datetime.datetime.strptime(target_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    end_timestamp = int(end_of_day.timestamp())

    before_signature = None
    print(f"Searching for the starting signature closest to {target_date}...")

    while True:
        params = {"limit": 100}
        if before_signature:
            params["before"] = before_signature

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet_address, params]
        }

        response = safe_request(rpc_url, payload, headers)
        result = response.get("result", [])

        if not result:
            print("No transactions found.")
            return None

        for tx in result:
            block_time = tx.get("blockTime", 0)
            signature = tx.get("signature", "N/A")

            if block_time <= end_timestamp:
                print(f"Found starting signature: {signature}")
                return signature

        before_signature = result[-1]["signature"]
        print(f"Continuing search... Before Signature: {before_signature}")