import pandas as pd

# File paths
input_file = "input.csv"  # Replace with your input file name
output_file = "output_with_balance_change.csv"

def calculate_balance_change(input_path, output_path):
    """Reads a CSV, calculates balance changes, and writes a new CSV."""
    try:
        # Read the CSV file
        df = pd.read_csv(input_path, sep=",", skiprows=1)  # Skip first row with "sep="

        # Rename columns for safety
        df.columns = ["Time", "Identity account"]

        # Ensure 'Identity account' is numeric
        df["Identity account"] = pd.to_numeric(df["Identity account"], errors="coerce")

        # Calculate change in balance
        df["Balance Change"] = df["Identity account"].diff().fillna(0)

        # Save to a new CSV file
        df.to_csv(output_path, index=False)
        print(f"✅ New file with balance changes saved to: {output_path}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    # Run the function
    calculate_balance_change(input_file, output_file)
    