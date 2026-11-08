

import pandas as pd
from pathlib import Path

from parser.dispatcher import parse_remark


INPUT_FILE = Path("data/input/data.csv")
OUTPUT_DIR = Path("data/output")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Reading ICICI statement...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "Transaction Posted Date",
        "Transaction Remarks",
        "Withdrawal Amt (INR)",
        "Deposit Amt (INR)",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    print("Total transactions:", len(df))

    # Parse transaction remarks
    remarks = df["Transaction Remarks"].fillna("")
    parsed_df = pd.DataFrame(
        remarks.apply(parse_remark).tolist(),
        index=df.index
    )

    # Build ONLY the required six columns
    final_df = pd.DataFrame({
        "Transaction Posted Date": df["Transaction Posted Date"],
        "Transaction Remarks": df["Transaction Remarks"],
        "Withdrawal Amount": df["Withdrawal Amt (INR)"],
        "Deposit Amount": df["Deposit Amt (INR)"],
        "merchant_candidate": parsed_df.get(
            "merchant_candidate",
            pd.Series(index=df.index, dtype="object")
        ),
        "beneficiary_candidate": parsed_df.get(
            "beneficiary_candidate",
            pd.Series(index=df.index, dtype="object")
        )
    })

    # Export Excel
    output_file = OUTPUT_DIR / "icici_transaction_report.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        final_df.to_excel(
            writer,
            sheet_name="Transactions",
            index=False
        )

        sheet = writer.sheets["Transactions"]
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions

        for column in sheet.columns:
            max_length = max(
                len(str(cell.value or ""))
                for cell in column
            )
            sheet.column_dimensions[
                column[0].column_letter
            ].width = min(max_length + 3, 45)

    print("\nSUCCESS!")
    print("File:", output_file.resolve())
    print("Rows:", len(final_df))
    print("Columns:", list(final_df.columns))


if __name__ == "__main__":
    main()
