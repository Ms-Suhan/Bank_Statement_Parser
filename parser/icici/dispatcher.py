from parser.icici.upi import parse_upi
from parser.icici.imps import parse_imps
from parser.icici.neft import parse_neft
from parser.icici.rtgs import parse_rtgs

from parser.icici.other import (
    parse_internal,
    parse_inft,
    parse_bill,
    parse_gib
)


def parse_remark(remark):

    remark = str(remark).strip()

    if not remark:
        return {
            "transaction_type": "UNKNOWN",
            "original_remark": remark,
            "status": "empty"
        }

    upper = remark.upper()

    # UPI including reversals
    if upper.startswith("UPI/") or upper.startswith("UPI/RVSL"):
        return parse_upi(remark)

    elif upper.startswith("MMT/IMPS/"):
        return parse_imps(remark)

    elif upper.startswith("NEFT-"):
        return parse_neft(remark)

    elif upper.startswith("RTGS-"):
        return parse_rtgs(remark)

    elif upper.startswith("TRFR FROM:"):
        return parse_internal(remark)

    elif upper.startswith("INF/INFT/"):
        return parse_inft(remark)

    elif upper.startswith("BIL/"):
        return parse_bill(remark)

    elif upper.startswith("GIB/"):
        return parse_gib(remark)

    return {
        "transaction_type": "UNKNOWN",
        "original_remark": remark,
        "status": "manual_review"
    }
