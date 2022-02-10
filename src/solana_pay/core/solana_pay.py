from solana_pay.core.models import PaymentRequest
from solana_pay.core.sol_payment_transaction_builder import SolPaymentTransactionBuilder
from solana_pay.core.spl_payment_transaction_builder import SplPaymentTransactionBuilder
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.transaction import Transaction


class SolanaPay:
    def __init__(self, endpoint: str) -> None:
        self._rpc_client = Client(endpoint)
    
    def create_transfer_transaction(self, payer: PublicKey, payment_request: PaymentRequest) -> Transaction:
        if payment_request.spl_token:
            return SplPaymentTransactionBuilder(self._rpc_client).create(payer, payment_request)
        else:
            return SplPaymentTransactionBuilder(self._rpc_client).create(payer, payment_request)
        