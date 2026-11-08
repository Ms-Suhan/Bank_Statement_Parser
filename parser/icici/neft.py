from parser.utils import make_result


def parse_neft(remark):
    remark = str(remark).strip()

    # Expected format:
    # NEFT-REFERENCE-BENEFICIARY-ACCOUNT-BANK-IFSC

    parts = [part.strip() for part in remark.split("-")]

    if len(parts) >= 6 and parts[0].upper() == "NEFT":
        beneficiary = parts[2] or None

        if beneficiary:
            return make_result(
                remark=remark,
                transaction_type="NEFT",
                beneficiary=beneficiary,
                status="rule_matched"
            )

    return make_result(
        remark=remark,
        transaction_type="NEFT",
        status="manual_review"
    )
