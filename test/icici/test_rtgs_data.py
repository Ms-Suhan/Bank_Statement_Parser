import pandas as pd
from pathlib import Path
from parser.dispatcher import parse_remark

df = pd.read_csv("data/input/data.csv")

rtgs_df = df[
    df["Transaction Remarks"]
    .fillna("")
    .str.strip()
    .str.upper()
    .str.startswith("RTGS-")
].copy()

results = rtgs_df["Transaction Remarks"].apply(parse_remark)

parsed_df = pd.DataFrame(results.tolist())

parsed_df.insert(
    0,
    "Date",
    rtgs_df["Transaction Posted Date"].values
)

parsed_df["Withdrawal"] = rtgs_df["Withdrawal Amt (INR)"].values
parsed_df["Deposit"] = rtgs_df["Deposit Amt (INR)"].values

print("\nTotal RTGS transactions:", len(parsed_df))
print("\nParsing status:")
print(parsed_df["status"].value_counts())

print("\nExtracted beneficiaries:")
print(parsed_df["beneficiary_candidate"].to_string(index=False))

print("\nManual review:")
print(
    parsed_df.loc[
        parsed_df["status"] == "manual_review",
        "original_remark"
    ].to_string(index=False)
)

Path("data/output").mkdir(parents=True, exist_ok=True)

parsed_df.to_csv(
    "data/output/rtgs_parser_results.csv",
    index=False
)

print("\nSaved: data/output/rtgs_parser_results.csv")
