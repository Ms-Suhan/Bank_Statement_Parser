import pandas as pd
from pathlib import Path
from parser.dispatcher import parse_remark

df = pd.read_csv("data/input/data.csv")

remarks = df["Transaction Remarks"].fillna("").str.strip()

internal_df = df[
    remarks.str.upper().str.startswith("TRFR FROM:")
].copy()

results = internal_df["Transaction Remarks"].apply(parse_remark)

parsed_df = pd.DataFrame(results.tolist())

parsed_df.insert(
    0, "Date",
    internal_df["Transaction Posted Date"].values
)

parsed_df["Withdrawal"] = internal_df["Withdrawal Amt (INR)"].values
parsed_df["Deposit"] = internal_df["Deposit Amt (INR)"].values

print("Total internal transfers:", len(parsed_df))
print("\nParsing status:")
print(parsed_df["status"].value_counts())

print("\nBeneficiaries:")
print(parsed_df["beneficiary_candidate"].to_string(index=False))

Path("data/output").mkdir(parents=True, exist_ok=True)

parsed_df.to_csv(
    "data/output/internal_parser_results.csv",
    index=False
)

print("\nSaved: data/output/internal_parser_results.csv")
