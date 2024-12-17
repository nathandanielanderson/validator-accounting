import requests
import time

def safe_request(url, payload, headers, retries=3, delay=2):
    """Send a POST request with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Max retries exceeded.")

def retry_on_failure(func, retries=3, delay=5):
    """Retry decorator for functions."""
    def wrapper(*args, **kwargs):
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
        raise Exception("Max retries exceeded.")
    return wrapper