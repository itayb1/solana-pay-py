from solana_pay import __version__
from solana_pay import PaymentRequest
from solana.publickey import PublicKey


def test_version():
    assert __version__ == '0.1.0'


def test_payment_request():
    payment_request = PaymentRequest(recipient=PublicKey("mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2kN"),
                                     amount=0,
                                     reference=[
                                         PublicKey("mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2KK")],
                                     message="test")
    assert payment_request.to_url() == "solana:mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2kN?amount=0&message=test&reference=mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2KK"


def test_payment_request_validators():
    try:
        payment_request = PaymentRequest(recipient=PublicKey("mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2kN"),
                                         amount=-5,
                                         reference=[
                                         PublicKey("mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2KK")],
                                         message="test")

    except Exception as e:
        assert type(e) == ValueError
    

def test_payment_request_from_url():
    try:
        url = "solana:mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2kN?amount=0&message=test&reference=mvines9iiHiQTysrwkJjGf2gb9Ex9jXJX8ns3qwf2KK"
        payment_request = PaymentRequest.from_url(url)
        print(payment_request)
    except Exception as e:
        pass
