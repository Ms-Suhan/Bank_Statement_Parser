

import pandas as pd
from pathlib import Path

from parser.union_bank.dispatcher import parse_remark


INPUT_FILE = Path("data/input/data_2.xlsx")

# Union Bank transaction headers are on Excel row 14

df = pd.read_excel(
    INPUT_FILE,
    header=0,
    engine="calamine"
)

# Clean column names
df.columns = [
    str(col).replace("\x00", "").strip()
    for col in df.columns
]

# Standardize column names
df = df.rename(columns={
    "Date": "Transaction Posted Date",
    "Remarks": "Transaction Remarks",
    "Withdrawals": "Withdrawal Amt (INR)",
    "Deposits": "Deposit Amt (INR)"
})

# Keep only actual transactions
df = df[df["Transaction Posted Date"].notna()].copy()
# Remove bank charge transactions
df = df[
    ~df["Transaction Remarks"]
    .fillna("")
    .str.strip()
    .str.startswith("Charges for PORD Customer", na=False)
].copy()


print("Transactions after filtering:", len(df))

print(
    "Remaining bank charge rows:",
    df["Transaction Remarks"]
    .fillna("")
    .str.startswith("Charges for PORD Customer")
    .sum()
)

print("Columns:", df.columns.tolist())
print("Total transactions:", len(df))



# Remove rows without transaction dates
#df = df[df["Transaction Posted Date"].notna()].copy()

# Parse narration
results = df["Transaction Remarks"].fillna("").apply(parse_remark)

parsed = pd.DataFrame(results.tolist(), index=df.index)

# Build common output format
final_df = pd.DataFrame({
    "Transaction Posted Date": df["Transaction Posted Date"],
    "Transaction Remarks": df["Transaction Remarks"],
    "Withdrawal Amount": df["Withdrawal Amt (INR)"],
    "Deposit Amount": df["Deposit Amt (INR)"],
    "merchant_candidate": parsed.get(
        "merchant_candidate",
        pd.Series(None, index=df.index)
    ),
    "beneficiary_candidate": parsed["beneficiary_candidate"]
})

# Display results
print("\nTotal transactions:", len(final_df))
print("\nTransaction types:")
print(parsed["transaction_type"].value_counts())

print("\nParsing status:")
print(parsed["status"].value_counts())

print("\nUnmatched transactions:")
print(
    final_df.loc[
        parsed["status"] == "manual_review",
        "Transaction Remarks"
    ].to_string(index=False)
)

# Export Excel
output = Path("data/output/union_bank_report.xlsx")
output.parent.mkdir(parents=True, exist_ok=True)

final_df.to_excel(output, index=False)

print("\nExcel generated:", output)
