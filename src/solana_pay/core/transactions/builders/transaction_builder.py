from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from solana.publickey import PublicKey
from solana_pay.common.consts import MEMO_PROGRAM_ID
from solana_pay.core.models import PaymentRequest
from solana.rpc.api import Client
from abc import ABC, abstractmethod


class TransactionBuilder(ABC):
    def __init__(self, rpc_client: Client):
        self._rpc_client = rpc_client
    
    def __call__(self, payer: PublicKey, payment_request: PaymentRequest) -> Transaction:
        transaction: Transaction = Transaction()
        transfer_instruction: TransactionInstruction = None
        transfer_instruction = self._create_transfer_instruction(payer, payment_request)
       
        self._add_reference_to_transfer_instruction(payment_request, transfer_instruction)
        
        if payment_request.memo:
            transaction.add(self._create_memo_instruction(payment_request))

        transaction.add(transfer_instruction)

        return transaction

    @abstractmethod
    def _create_transfer_instruction(self, payer: PublicKey, payment_request: PaymentRequest) -> TransactionInstruction:
        raise NotImplementedError() 

    def _create_memo_instruction(self, payment_request: PaymentRequest) -> TransactionInstruction:
        return TransactionInstruction(keys=[], program_id=MEMO_PROGRAM_ID, data=payment_request.memo.encode())

    def _add_reference_to_transfer_instruction(self, payment_request: PaymentRequest, transfer_instruction: TransactionInstruction):
        if payment_request.reference:
            if isinstance(payment_request.reference, list):
                for reference in payment_request.reference:
                    transfer_instruction.keys.append(
                        AccountMeta(reference, False, False))
            else:
                transfer_instruction.keys.append(
                    AccountMeta(payment_request.reference, False, False))