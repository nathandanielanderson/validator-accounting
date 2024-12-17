import json

def load_config(file_path="config.json"):
    """Load RPC URL and wallet address from a config file."""
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"]