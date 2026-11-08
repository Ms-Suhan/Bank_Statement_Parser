from parser.utils import make_result


def parse_rtgs(remark):
    remark = str(remark).strip()

    # Expected format:
    # RTGS-REFERENCE-BENEFICIARY-ACCOUNT-IFSC

    parts = [part.strip() for part in remark.split("-")]

    if len(parts) >= 5 and parts[0].upper() == "RTGS":
        beneficiary = parts[2] or None

        if beneficiary:
            return make_result(
                remark=remark,
                transaction_type="RTGS",
                beneficiary=beneficiary,
                status="rule_matched"
            )

    return make_result(
        remark=remark,
        transaction_type="RTGS",
        status="manual_review"
    )
