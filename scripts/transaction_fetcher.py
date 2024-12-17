import requests
from utils import safe_request, retry_on_failure

def fetch_transactions(wallet_address, rpc_url, starting_signature, limit=1000):
    """Fetch transactions starting from a specific signature."""
    headers = {"Content-Type": "application/json"}
    before_signature = starting_signature
    while True:
        params = {"limit": limit}
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
            break

        yield result
        before_signature = result[-1]["signature"]