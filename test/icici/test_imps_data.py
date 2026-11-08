import pandas as pd
from pathlib import Path
from parser.dispatcher import parse_remark

df = pd.read_csv("data/input/data.csv")

imps_df = df[
    df["Transaction Remarks"]
    .fillna("")
    .str.strip()
    .str.upper()
    .str.startswith("MMT/IMPS/")
].copy()

results = imps_df["Transaction Remarks"].apply(parse_remark)

parsed_df = pd.DataFrame(results.tolist())

parsed_df.insert(
    0,
    "Date",
    imps_df["Transaction Posted Date"].values
)

parsed_df["Withdrawal"] = imps_df["Withdrawal Amt (INR)"].values
parsed_df["Deposit"] = imps_df["Deposit Amt (INR)"].values

print("\nTotal IMPS transactions:", len(parsed_df))
print("\nTransaction types:")
print(parsed_df["transaction_type"].value_counts())

print("\nParsing status:")
print(parsed_df["status"].value_counts())

print("\nManual review transactions:")
print(
    parsed_df.loc[
        parsed_df["status"] == "manual_review",
        "original_remark"
    ].to_string(index=False)
)

Path("data/output").mkdir(parents=True, exist_ok=True)

parsed_df.to_csv(
    "data/output/imps_parser_results.csv",
    index=False
)

print("\nSaved: data/output/imps_parser_results.csv")
