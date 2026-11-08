def make_result(
        remark,
        transaction_type="UNKNOWN",
        reference=None,
        merchant=None,
        beneficiary=None,
        upi_id=None,
        bank=None,
        status="Manual_Review"
        ):
    return {
            "transaction_type": transaction_type,
            "reference": reference,
            "merchant_candidate": merchant,
            "beneficiary_candidate": beneficiary,
            "upi_id": upi_id,
            "bank": bank,
            "original_remark": remark,
            "status": status
            }
