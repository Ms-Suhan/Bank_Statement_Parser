

import re
from parser.utils import make_result


def make_union_result(
    remark,
    transaction_type,
    beneficiary=None,
    merchant=None,
    status="rule_matched"
):
    return make_result(
        remark=remark,
        transaction_type=transaction_type,
        beneficiary=beneficiary,
        merchant=merchant,
        status=status
    )


def parse_remark(remark):
    remark = str(remark).strip()

    if not remark:
        return make_union_result(
            remark,
            "UNKNOWN",
            status="manual_review"
        )

    upper = remark.upper()

    # IMPS debit and credit
    if upper.startswith(("IMPSAR/", "IMPSAB/")):
        parts = remark.split("/")

        if len(parts) >= 4:
            beneficiary = parts[2].strip()

            return make_union_result(
                remark,
                "IMPS",
                beneficiary=beneficiary or None
            )

    # RTGS debit
    if upper.startswith("RTGSO-"):
        name = re.sub(
            r"\s+[A-Z]{4,}[A-Z0-9]{10,}$",
            "",
            remark[6:].strip(),
            flags=re.IGNORECASE
        ).strip()

        if name:
            return make_union_result(remark, "RTGS", beneficiary=name)

    # RTGS credit
    if upper.startswith("RTGS:"):
        name = re.sub(
            r"\s+[A-Z]{4,}[A-Z0-9]{10,}$",
            "",
            remark[5:].strip(),
            flags=re.IGNORECASE
        ).strip()

        if name:
            return make_union_result(remark, "RTGS", beneficiary=name)

    # NEFT debit
    if upper.startswith("NEFT:ITDTAX REFUND"):
        return make_union_result(
            remark,
            "NEFT",
            beneficiary=None,
            status="manual_review"
    )

    if upper.startswith("NEFTO-"):
        name = re.sub(
            r"\s+\d{8,}$",
            "",
            remark[6:].strip()
        ).strip()

        if name:
            return make_union_result(remark, "NEFT", beneficiary=name)

    # NEFT credit
    if upper.startswith("NEFT:"):
        name = remark[5:].strip()

        name = re.sub(
            r"\s+[A-Z]{4,}[A-Z0-9]{8,}(?:\s+[A-Z]{4,}[A-Z0-9]{5,})?$",
            "",
            name,
            flags=re.IGNORECASE
        ).strip()

        if name:
            return make_union_result(remark, "NEFT", beneficiary=name)

    # eTXN debit and credit
    if upper.startswith("ETXN/"):
        parts = remark.split("/")

        if len(parts) >= 3:
            beneficiary = parts[2].strip()

            if beneficiary:
                return make_union_result(
                    remark,
                    "ETXN",
                    beneficiary=beneficiary
                )

    # Internal transfer
    if upper.startswith("TRANSFER FROM UBI AC"):
        beneficiary = re.sub(
            r"^TRANSFER FROM UBI AC\s*",
            "",
            remark,
            flags=re.IGNORECASE
        ).strip()

        if beneficiary:
            return make_union_result(
                remark,
                "INTERNAL_TRANSFER",
                beneficiary=beneficiary
            )

    # Bank charges
    if upper.startswith("CHARGES FOR PORD"):
        return make_union_result(
            remark,
            "BANK_CHARGE"
        )

    return make_union_result(
        remark,
        "UNKNOWN",
        status="manual_review"
    )
