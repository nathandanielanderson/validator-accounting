from config_loader import load_config
from signature_finder import find_starting_signature
from transaction_fetcher import fetch_transactions
from csv_writer import write_transactions_to_csv
import datetime

if __name__ == "__main__":
    # Load configuration
    RPC_URL, WALLET_ADDRESS = load_config()

    # Define starting date or take user input
    target_date = input("Enter the target date (YYYY-MM-DD) or press Enter to fetch the most recent transactions: ").strip()
    if target_date:
        print(f"Searching for transactions on {target_date}...")
        starting_signature = find_starting_signature(WALLET_ADDRESS, RPC_URL, target_date)
    else:
        print("No target date provided. Fetching the most recent transactions...")
        starting_signature = None  # No date means start with the latest transactions

    # Generate output file name
    if target_date:
        formatted_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").strftime("%y-%m-%d")
    else:
        formatted_date = datetime.datetime.now().strftime("%y-%m-%d")
    
    output_file = f"../output/{formatted_date}_{WALLET_ADDRESS}_TXs.csv"

    print(f"Fetching transactions and saving to {output_file}...\n")
    for batch in fetch_transactions(WALLET_ADDRESS, RPC_URL, starting_signature):
        for readable_time, signature in write_transactions_to_csv(output_file, batch):
            print(f"Saved Transaction: {readable_time} | {signature}")