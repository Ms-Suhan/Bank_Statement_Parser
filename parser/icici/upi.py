from parser.utils import make_result
import re


def parse_upi(remark):
    remark = str(remark).strip()

    is_reversal = remark.upper().startswith("UPI/RVSL")

    if is_reversal:
        remark_for_parsing = re.sub(
            r"^UPI/RVSL",
            "UPI/",
            remark,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        remark_for_parsing = remark

    parts = [p.strip() for p in remark_for_parsing.split("/")]

    transaction_type = "UPI_REVERSAL" if is_reversal else "UPI"

    # Format A:
    # UPI/reference/merchant/UPI_ID//bank_reference
    if (
        len(parts) >= 4
        and parts[0].upper() == "UPI"
        and parts[1].isdigit()
        and parts[2].upper() != "UPI"
    ):
        return make_result(
            remark=remark,
            transaction_type=transaction_type,
            reference=parts[1],
            merchant=parts[2] or None,
            beneficiary=parts[3] or None,
            upi_id=parts[3] if "@" in parts[3] else None,
            bank=None,
            status="rule_matched"
        )

    # Format B:
    # UPI/reference/UPI/UPI_ID/BANK/...
    if (
        len(parts) >= 6
        and parts[0].upper() == "UPI"
        and parts[1].isdigit()
        and parts[2].upper() == "UPI"
    ):
        return make_result(
            remark=remark,
            transaction_type=transaction_type,
            reference=parts[1],
            beneficiary=None,
            merchant=None,
            upi_id=parts[3] if "@" in parts[3] else None,
            bank=parts[4] or None,
            status="rule_matched"
        )

    # Format C:
    # UPI/name/UPI_ID/code/BANK/reference/...
    if (
        len(parts) >= 7
        and parts[0].upper() == "UPI"
        and "@" in parts[2]
        and parts[5].isdigit()
    ):
        return make_result(
            remark=remark,
            transaction_type=transaction_type,
            reference=parts[5],
            beneficiary=parts[1] or None,
            merchant=None,
            upi_id=parts[2],
            bank=parts[4] or None,
            status="rule_matched"
        )

    return make_result(
        remark=remark,
        transaction_type=transaction_type,
        status="manual_review"
    )
