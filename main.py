import requests
import datetime
import csv
import json
import os


# Configuration loader
def load_config(file_path="config.json"):
    """Load API URL, wallet address, and API key from a config file."""
    with open(file_path, "r") as file:
        config = json.load(file)
    return config["rpc_url"], config["wallet_address"], config["api_key"]


# Fetch balance at a specific timestamp
def fetch_balance(wallet_address, rpc_url, api_key, timestamp):
    """Fetch the balance of the wallet at a specific timestamp."""
    url = f"{rpc_url}/v0/balances?api-key={api_key}"
    params = {
        "addresses": [wallet_address],
        "at": timestamp
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        balances = response.json()
        return balances[0]['balance']  # Assuming the response contains balances for one wallet
    except Exception as e:
        print(f"⚠️ Error fetching balance at {timestamp}: {e}")
        return None


# Generate a list of daily timestamps
def generate_daily_timestamps(start_date, end_date):
    """Generate a list of timestamps for each day in the date range."""
    current_date = start_date
    while current_date <= end_date:
        # Timestamp at the start of the day (00:00:00 UTC)
        yield int(current_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        current_date += datetime.timedelta(days=1)


# Write daily balances to CSV
def write_daily_balances_to_csv(wallet_address, daily_balances):
    """Write the daily balances to a CSV file."""
    file_name = f"output/daily_balances_{wallet_address}.csv"
    os.makedirs("output", exist_ok=True)

    with open(file_name, mode="w", newline="") as csvfile:
        fieldnames = ["Date (UTC)", "Balance (Lamports)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for date, balance in daily_balances:
            writer.writerow({"Date (UTC)": date, "Balance (Lamports)": balance})

    print(f"✅ Daily balances saved to {file_name}.")


# Main script
def main():
    print("🚀 Starting Daily Balance Fetcher...")

    # Load configuration
    rpc_url, wallet_address, api_key = load_config()
    print(f"✅ Config Loaded - Wallet Address: {wallet_address}")

    # Date range
    start_date = datetime.datetime(2024, 12, 1, tzinfo=datetime.timezone.utc)  # Change as needed
    end_date = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    print(f"📅 Fetching daily balances from {start_date.date()} to {end_date.date()}...")

    # Fetch daily balances
    daily_balances = []
    for timestamp in generate_daily_timestamps(start_date, end_date):
        date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
        print(f"📡 Fetching balance for {date}...")
        balance = fetch_balance(wallet_address, rpc_url, api_key, timestamp)
        if balance is not None:
            daily_balances.append((date, balance))

    # Write balances to CSV
    print("💾 Writing daily balances to CSV...")
    write_daily_balances_to_csv(wallet_address, daily_balances)

    print("✅ Daily balance fetch and save completed!")


if __name__ == "__main__":
    main()