from typing import List, Optional, Union
from solana_pay.core.models import PaymentRequest
from solana_pay.core.transactions import SplTransactionBuilder, SolTransactionBuilder
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.transaction import Transaction, TransactionSignature
from solana.rpc.commitment import Commitment
from solana_pay.common.exceptions import FindTransactionError
from solana_pay.core.transactions import SplTransactionValidator, SolTransactionValidator
from solana_pay.core.transactions.validators.transaction_validator import TransactionDetails


class SolanaPay:
    def __init__(self, endpoint: str) -> None:
        self._rpc_client = Client(endpoint)
        self._sol_transaction_builder = SolTransactionBuilder(self._rpc_client)
        self._spl_transaction_builder = SplTransactionBuilder(self._rpc_client)
        self._sol_transaction_validator = SolTransactionValidator(self._rpc_client)
        self._spl_transaction_validator = SplTransactionValidator(self._rpc_client)

    def create_transfer_transaction(self, payer: PublicKey, payment_request: PaymentRequest) -> Transaction:
        if payment_request.spl_token:
            return self._spl_transaction_builder.create(payer, payment_request)
        else:
            return self._sol_transaction_builder.create(payer, payment_request)

    def find_transaction_signature(self, reference: PublicKey, before: Optional[TransactionSignature] = None, limit: Optional[int] = 1000, until: Optional[TransactionSignature] = None, commitment: Commitment = None):
        signatures = self._rpc_client.get_signatures_for_address(reference, before, until, limit, commitment).get('result')
        if signatures == None or len(signatures) == 0:
            raise FindTransactionError("Not found.")
        
        if len(signatures) < limit or len(signatures) < 1000:
            return signatures[len(signatures) - 1]
    
    def validate_transaction_signature(self, signature: TransactionSignature,  recipient: PublicKey, amount: float, spl_token: Optional[PublicKey] = None, reference: Optional[Union[List[PublicKey], PublicKey]] = None, commitment: Optional[Commitment] = None):
        validation_args = {
            "signature": signature,
            "recipient": recipient,
            "amount": amount,
            "spl_token": spl_token,
            "reference": reference,
            "commitment": commitment
        }
        transaction_details = TransactionDetails(**validation_args)
        if spl_token:
            return self._spl_transaction_validator(transaction_details)
        else:
            return self._sol_transaction_validator(transaction_details)
