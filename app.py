

import streamlit as st
import pandas as pd

from io import BytesIO

# Bank-specific parsers
from parser.icici.dispatcher import parse_remark as parse_icici
from parser.union_bank.dispatcher import parse_remark as parse_union_bank


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="ASWE Bank Statement Parser",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 ASWE Bank Statement Parser")
st.caption(
    "Upload your bank statement and extract transaction beneficiaries."
)

st.divider()


# ==================================================
# 1. BANK SELECTION AND FILE UPLOAD
# ==================================================

bank = st.selectbox(
    "Select your bank",
    ["ICICI Bank", "Union Bank"]
)

if bank == "ICICI Bank":

    accepted_types = ["csv"]

    st.info("Upload your ICICI Bank CSV statement.")

else:

    accepted_types = ["csv", "xls", "xlsx"]

    st.info(
        "Upload your Union Bank statement in CSV, XLS or XLSX format."
    )


uploaded_file = st.file_uploader(
    "Upload bank statement",
    type=accepted_types,
    key="statement_uploader"
)


# ==================================================
# 2. LOAD STATEMENT
# ==================================================

def load_statement(file, selected_bank):

    file_name = file.name.lower()

    # ----------------------------------------------
    # ICICI BANK
    # ----------------------------------------------

    if selected_bank == "ICICI Bank":

        if not file_name.endswith(".csv"):
            raise ValueError(
                "ICICI Bank supports CSV files only."
            )

        df = pd.read_csv(file)

    # ----------------------------------------------
    # UNION BANK
    # ----------------------------------------------

    elif selected_bank == "Union Bank":

        if file_name.endswith(".csv"):

            df = pd.read_csv(file)

        elif file_name.endswith((".xls", ".xlsx")):

            df = pd.read_excel(
                file,
                header=0,
                engine="calamine"
            )

        else:

            raise ValueError(
                "Unsupported Union Bank file format."
            )

        # Clean column names
        df.columns = [
            str(col).replace("\x00", "").strip()
            for col in df.columns
        ]

        # Standardize Union Bank columns
        df = df.rename(columns={
            "Date": "Transaction Posted Date",
            "Remarks": "Transaction Remarks",
            "Withdrawals": "Withdrawal Amt (INR)",
            "Deposits": "Deposit Amt (INR)"
        })

    else:

        raise ValueError("Unsupported bank selected.")

    return df


# ==================================================
# 3. PROCESS STATEMENT
# ==================================================

def process_statement(df, selected_bank):

    required_columns = [
        "Transaction Posted Date",
        "Transaction Remarks",
        "Withdrawal Amt (INR)",
        "Deposit Amt (INR)"
    ]

    # Check required columns
    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df = df.copy()

    # Remove rows without transaction dates
    df = df[
        df["Transaction Posted Date"].notna()
    ].copy()

    # ----------------------------------------------
    # SELECT BANK PARSER
    # ----------------------------------------------

    if selected_bank == "ICICI Bank":

        parse_function = parse_icici

    elif selected_bank == "Union Bank":

        parse_function = parse_union_bank

        # Remove bank charge transactions
        charge_mask = (
            df["Transaction Remarks"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.startswith(
                "Charges for PORD Customer",
                na=False
            )
        )

        df = df[~charge_mask].copy()

    # ----------------------------------------------
    # PARSE TRANSACTION REMARKS
    # ----------------------------------------------

    remarks = df["Transaction Remarks"].fillna("")

    results = remarks.apply(parse_function)

    parsed = pd.DataFrame(
        results.tolist(),
        index=df.index
    )

    # Ensure candidate columns exist
    if "merchant_candidate" not in parsed.columns:

        parsed["merchant_candidate"] = None

    if "beneficiary_candidate" not in parsed.columns:

        parsed["beneficiary_candidate"] = None

    # ----------------------------------------------
    # UNION BANK TAX REFUND HANDLING
    # ----------------------------------------------

    if selected_bank == "Union Bank":

        tax_refund_mask = (
            remarks.astype(str)
            .str.strip()
            .str.upper()
            .str.startswith(
                "NEFT:ITDTAX REFUND"
            )
        )

        # Preserve original narration.
        # Do not extract a beneficiary from tax refunds.
        parsed.loc[
            tax_refund_mask,
            "beneficiary_candidate"
        ] = None

    # ----------------------------------------------
    # BUILD FINAL SIX-COLUMN REPORT
    # ----------------------------------------------

    final_df = pd.DataFrame({

        "Transaction Posted Date":
            df["Transaction Posted Date"],

        "Transaction Remarks":
            df["Transaction Remarks"],

        "Withdrawal Amount":
            df["Withdrawal Amt (INR)"],

        "Deposit Amount":
            df["Deposit Amt (INR)"],

        "merchant_candidate":
            parsed["merchant_candidate"],

        "beneficiary_candidate":
            parsed["beneficiary_candidate"]

    })

    return final_df.reset_index(drop=True)


# ==================================================
# 4. CREATE EXCEL REPORT
# ==================================================

def create_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Transactions",
            index=False
        )

        sheet = writer.sheets["Transactions"]

        # Freeze header row
        sheet.freeze_panes = "A2"

        # Enable filters
        sheet.auto_filter.ref = sheet.dimensions

        # Automatically adjust column widths
        for column in sheet.columns:

            max_length = max(
                len(str(cell.value or ""))
                for cell in column
            )

            sheet.column_dimensions[
                column[0].column_letter
            ].width = min(max_length + 3, 45)

    output.seek(0)

    return output


# ==================================================
# 5. PROCESS UPLOADED FILE
# ==================================================

if uploaded_file:

    if st.button(
        "Process Statement",
        type="primary"
    ):

        try:

            with st.spinner("Processing transactions..."):

                # Load statement
                df = load_statement(
                    uploaded_file,
                    bank
                )

                # Process statement
                result = process_statement(
                    df,
                    bank
                )

                # Save results
                st.session_state["result"] = result

                st.session_state["processed_bank"] = bank

                st.session_state["processed_filename"] = (
                    uploaded_file.name
                )

            st.success(
                "Statement processed successfully!"
            )

        except Exception as e:

            st.error(f"Error: {e}")


# ==================================================
# 6. DISPLAY RESULTS
# ==================================================

if "result" in st.session_state:

    result = st.session_state["result"]

    st.divider()

    st.subheader("Processing Results")

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Transactions",
        len(result)
    )

    col2.metric(
        "Beneficiaries Identified",
        result["beneficiary_candidate"].notna().sum()
    )

    st.caption(
        f"Processed bank: {st.session_state['processed_bank']}"
    )

    st.subheader("Transaction Preview")

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # DOWNLOAD EXCEL
    # ----------------------------------------------

    excel_file = create_excel(result)

    bank_filename = (
        st.session_state["processed_bank"]
        .lower()
        .replace(" ", "_")
    )

    st.download_button(
        label="Download Excel Report",
        data=excel_file,
        file_name=f"{bank_filename}_transaction_report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        type="primary"
    )

    # ==================================================
# 7. FOOTER
# ==================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align: center;
        color: #888888;
        font-size: 13px;
        padding: 10px 0 5px 0;
    ">
        Made with <span style="color: #e25555;">♥</span> by
        <strong style="color: inherit;">Suhan</strong>
        &nbsp;|&nbsp;
        <a href="https://github.com/Ms-Suhan"
           target="_blank"
           style="color: #888888; text-decoration: none;">
            GitHub
        </a>
        &nbsp;|&nbsp;
        <a href="https://www.linkedin.com/in/suhan-ms-a836b62a2/"
           target="_blank"
           style="color: #888888; text-decoration: none;">
            LinkedIn
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
