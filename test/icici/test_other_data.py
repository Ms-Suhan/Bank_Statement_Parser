

import pandas as pd
from pathlib import Path
from parser.dispatcher import parse_remark

df = pd.read_csv("data/input/data.csv")

remarks = df["Transaction Remarks"].fillna("").str.strip()

prefixes = {
    "INFT": "INF/INFT/",
    "BILL": "BIL/",
    "GIB": "GIB/"
}

all_results = []

for name, prefix in prefixes.items():

    subset = df[
        remarks.str.upper().str.startswith(prefix)
    ].copy()

    results = subset["Transaction Remarks"].apply(parse_remark)

    parsed = pd.DataFrame(results.tolist())

    parsed.insert(
        0,
        "Date",
        subset["Transaction Posted Date"].values
    )

    parsed["Withdrawal"] = subset["Withdrawal Amt (INR)"].values
    parsed["Deposit"] = subset["Deposit Amt (INR)"].values

    print(f"\n===== {name} =====")
    print("Total:", len(parsed))
    print("\nStatus:")
    print(parsed["status"].value_counts())

    print("\nBeneficiaries:")
    print(parsed["beneficiary_candidate"].to_string(index=False))

    all_results.append(parsed)

final_df = pd.concat(all_results, ignore_index=True)

Path("data/output").mkdir(parents=True, exist_ok=True)

final_df.to_csv(
    "data/output/other_parser_results.csv",
    index=False
)

print("\nSaved: data/output/other_parser_results.csv")
