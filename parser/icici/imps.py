from parser.utils import make_result


def parse_imps(remark):
    remark = str(remark).strip()
    parts = [part.strip() for part in remark.split("/")]

    # Expected format:
    # MMT/IMPS/REFERENCE/DETAILS/BENEFICIARY/IFSC

    if (
        len(parts) >= 6
        and parts[0].upper() == "MMT"
        and parts[1].upper() == "IMPS"
    ):
        beneficiary = parts[4] or None

        if beneficiary:
            return make_result(
                remark=remark,
                transaction_type="IMPS",
                beneficiary=beneficiary,
                status="rule_matched"
            )

    return make_result(
        remark=remark,
        transaction_type="IMPS",
        status="manual_review"
    )
