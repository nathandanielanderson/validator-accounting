import csv
import datetime

def write_transactions_to_csv(output_file, transactions):
    """Write fetched transactions to a CSV file."""
    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Block Time (UTC)", "Signature"])
        writer.writeheader()

        for tx in transactions:
            block_time = tx.get("blockTime", 0)
            signature = tx.get("signature", "N/A")
            readable_time = datetime.datetime.fromtimestamp(block_time, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')

            writer.writerow({"Block Time (UTC)": readable_time, "Signature": signature})
            yield readable_time, signature