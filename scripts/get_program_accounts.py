import requests
import json

# Load configuration
def load_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

# Fetch program accounts
def fetch_program_accounts(rpc_url, identity_account):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getProgramAccounts",
        "params": [
            identity_account,
            {"encoding": "jsonParsed"}
        ]
    }
    response = requests.post(rpc_url, json=payload)
    if response.status_code != 200:
        print(f"⚠️ Error fetching program accounts: {response.status_code}")
        return None

    return response.json()

# Main function
def main():
    print("🚀 Fetching Program Accounts...")

    # Load configuration
    config = load_config()
    rpc_url = config["RPC_URL"]
    identity_account = config["VOTE_ACCOUNT"]  # Add this to your config.json

    # Fetch program accounts
    result = fetch_program_accounts(rpc_url, identity_account)

    if result:
        print("✅ Program Accounts:")
        print(json.dumps(result, indent=4))  # Pretty print JSON
    else:
        print("⚠️ No program accounts found.")

if __name__ == "__main__":
    main()