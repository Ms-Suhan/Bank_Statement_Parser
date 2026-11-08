import pandas as pd
from pathlib import Path

from parser.dispatcher import parse_remark

# Load CSV
df = pd.read_csv("data/input/data.csv")

# Keep only UPI transactions
upi_df = df[
    df["Transaction Remarks"]
    .fillna("")
    .str.strip()
    .str.upper()
    .str.startswith("UPI/")
].copy()

# Parse remarks
results = upi_df["Transaction Remarks"].apply(
    parse_remark
)

parsed_df = pd.DataFrame(results.tolist())

# Retain transaction details
parsed_df.insert(
    0,
    "Date",
    upi_df["Transaction Posted Date"].values
)

parsed_df["Withdrawal"] = (
    upi_df["Withdrawal Amt (INR)"].values
)

parsed_df["Deposit"] = (
    upi_df["Deposit Amt (INR)"].values
)

# Statistics
print("Total UPI transactions:", len(parsed_df))

print("\nTransaction types:")
print(parsed_df["transaction_type"].value_counts())

print("\nParser status:")
print(parsed_df["status"].value_counts())

# Unknown transactions
print("\nTransactions requiring review:")

print(
    parsed_df[
        parsed_df["status"] == "manual_review"
    ]["original_remark"].to_string(index=False)
)

# Export
Path("data/output").mkdir(
    parents=True,
    exist_ok=True
)

parsed_df.to_csv(
    "data/output/upi_parser_results.csv",
    index=False
)

print("\nResults exported successfully!")
