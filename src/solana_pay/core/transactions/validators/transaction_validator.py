from dataclasses import dataclass
from solana.transaction import TransactionSignature
from solana.publickey import PublicKey
from solana_pay.common.exceptions import ValidateTransactionError
from solana_pay.common.consts import LAMPORTS_PER_SOL
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from typing import Optional, Union, List, Dict


@dataclass
class TransactionDetails:
    signature: TransactionSignature
    recipient: PublicKey
    amount: float
    spl_token: Optional[PublicKey] = None
    reference: Optional[Union[List[PublicKey], PublicKey]] = None
    commitment: Optional[Commitment] = None


class TransactionValidator:
    def __init__(self, rpc_client: Client):
        self._rpc_client = rpc_client

    def __call__(self, transaction_details: TransactionDetails):
        raise NotImplementedError()
 
    @staticmethod
    def _validate_amount(pre_amount, post_amount, amount):
        if (post_amount - pre_amount < amount):
            raise ValidateTransactionError("Amount was not transferred.")

    @staticmethod
    def _validate_reference(reference, transaction_keys):
        if isinstance(reference, PublicKey):
            reference = [reference]
        
        for pk in reference:
            if not str(pk) in transaction_keys:
                raise ValidateTransactionError(f"The reference public key {pk} was not found.")


