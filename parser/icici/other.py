

from parser.utils import make_result
import re


def parse_internal(remark):
    remark = str(remark).strip()

    match = re.match(r"TRFR\s+FROM:\s*(.+)$", remark, re.IGNORECASE)

    if match:
        beneficiary = match.group(1).strip()

        return make_result(
            remark=remark,
            transaction_type="INTERNAL_TRANSFER",
            beneficiary=beneficiary or None,
            status="rule_matched" if beneficiary else "manual_review"
        )

    return make_result(
        remark=remark,
        transaction_type="INTERNAL_TRANSFER",
        status="manual_review"
    )


def parse_inft(remark):
    remark = str(remark).strip()

    match = re.search(
        r"from\s+VANGHEE/([^/]+)$",
        remark,
        re.IGNORECASE
    )

    if match:
        beneficiary = match.group(1).strip()

        return make_result(
            remark=remark,
            transaction_type="INFT",
            beneficiary=beneficiary or None,
            status="rule_matched" if beneficiary else "manual_review"
        )

    return make_result(
        remark=remark,
        transaction_type="INFT",
        status="manual_review"
    )


def parse_bill(remark):
    remark = str(remark).strip()
    parts = [part.strip() for part in remark.split("/")]

    if len(parts) >= 4 and parts[0].upper() == "BIL":

        subtype = parts[1].upper()

        if subtype == "ONL":
            beneficiary = parts[3].strip()

        elif subtype == "INFT" and len(parts) >= 5:
            beneficiary = parts[-1].strip()

        else:
            beneficiary = None

        if beneficiary:
            return make_result(
                remark=remark,
                transaction_type="BILL_PAYMENT",
                beneficiary=beneficiary,
                status="rule_matched"
            )

    return make_result(
        remark=remark,
        transaction_type="BILL_PAYMENT",
        status="manual_review"
    )


def parse_gib(remark):
    remark = str(remark).strip()
    parts = [part.strip() for part in remark.split("/")]

    if len(parts) >= 3 and parts[0].upper() == "GIB":
        department = parts[2].strip()

        return {
            "transaction_type": "GOVERNMENT_PAYMENT",
            "beneficiary_candidate": None,
            "government_department": department or None,
            "original_remark": remark,
            "status": "rule_matched" if department else "manual_review"
        }

    return {
        "transaction_type": "GOVERNMENT_PAYMENT",
        "beneficiary_candidate": None,
        "government_department": None,
        "original_remark": remark,
        "status": "manual_review"
    }
