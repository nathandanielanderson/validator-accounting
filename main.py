import requests
from scripts.config_loader import load_config
from scripts.csv_writer import write_transactions_to_csv
import sys

def fetch_transactions(wallet_address, rpc_url):
    """Fetch transactions starting from the most recent one."""
    headers = {"Content-Type": "application/json"}
    before_signature = None
    batch_limit = 100
    