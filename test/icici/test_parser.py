from parser.dispatcher import parse_remark


def test_upi():
    remark = (
        "UPI/110569425613/HennurRoadcemen/"
        "msadhamsispat.e//ICIeca3b0d4d7d9418682979d41aadde48c"
    )

    result = parse_remark(remark)

    assert result["transaction_type"] == "UPI"
    assert result["merchant_candidate"] == "HennurRoadcemen"


def test_imps():
    remark = (
        "MMT/IMPS/624516017780/"
        "85080249 by MOS/ANJINAYYA/SBIN0011137"
    )

    result = parse_remark(remark)

    assert result["transaction_type"] == "IMPS"
    assert result["beneficiary_candidate"] == "ANJINAYYA"


def test_neft():
    remark = (
        "NEFT-HDFCH01234793433-RED BUTTERFLY "
        "PRIVATE LIMITED-0001-50200122594473-HDFC0000353"
    )

    result = parse_remark(remark)

    assert result["transaction_type"] == "NEFT"
    assert result["beneficiary_candidate"] == (
        "RED BUTTERFLY PRIVATE LIMITED"
    )


def test_rtgs():
    remark = (
        "RTGS-UBINR22026092401189212-"
        "ASWE CONSTRUCTIONS AND ENGINEERING-"
        "233711100001343-UBIN0823376"
    )

    result = parse_remark(remark)

    assert result["transaction_type"] == "RTGS"


def test_unknown():
    result = parse_remark("SOME UNKNOWN TRANSACTION")

    assert result["status"] == "manual_review"

def test_upi_reversal():

    remark = (
        "UPI/RVSL110707902128/"
        "Rabenggworks/XX1227@icici//ICI10a575b837584d02a8178adc4a381d90"
    )

    result = parse_remark(remark)

    assert result["transaction_type"] == "UPI_REVERSAL"
    assert result["reference"] == "110707902128"
    assert result["merchant_candidate"] == "Rabenggworks"


def test_upi_fdr():

    remark = (
        "UPI/NEMAN SHAR/XXarif@oksbi/"
        "fdr/State Bank/625885789257/"
        "SBI617e7257a1de405f95743bb735838998"
    )

    result = parse_remark(remark)

    assert result["beneficiary_candidate"] == "NEMAN SHAR"
    assert result["reference"] == "625885789257"


def test_upi_sd():

    remark = (
        "UPI/NEMAN SHAR/XXarif@oksbi/"
        "sd/State Bank/625941862307/"
        "SBI043e452b2cf04d89948bb4ec43c6dee3"
    )

    result = parse_remark(remark)

    assert result["beneficiary_candidate"] == "NEMAN SHAR"

def test_imps_parser():
    remark = (
        "MMT/IMPS/624516017780/"
        "85080249 by MOS/ANJINAYYA/SBIN0011137"
    )

    result = parse_remark(remark)

    assert result["transaction_type"] == "IMPS"
    assert result["beneficiary_candidate"] == "ANJINAYYA"
    assert result["status"] == "rule_matched"

def test_internal_transfer():
    remark = "TRFR FROM: NEELACHAL BUILDERS PRIVATE LIMITED"

    result = parse_remark(remark)

    assert result["transaction_type"] == "INTERNAL_TRANSFER"
    assert result["beneficiary_candidate"] == (
        "NEELACHAL BUILDERS PRIVATE LIMITED"
    )
    assert result["status"] == "rule_matched"


def test_internal_transfer_with_extra_spaces():
    remark = " TRFR FROM:NEELACHAL BUILDERS PRIVATE LIMITED"

    result = parse_remark(remark)

    assert result["beneficiary_candidate"] == (
        "NEELACHAL BUILDERS PRIVATE LIMITED"
    )
    assert result["status"] == "rule_matched"
