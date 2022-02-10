from ast import Raise
from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from solana.publickey import PublicKey
from solana_pay.common.exceptions import CreatePaymentTransactionError
from solana_pay.common.utils.helpers import find_decimals
from solana_pay.common.consts import MEMO_PROGRAM_ID, SOL_DECIMALS, LAMPORTS_PER_SOL
from solana_pay.core.models import PaymentRequest
from solana.rpc.api import Client
from spl.token.client import Token
from spl.token.instructions import get_associated_token_address, transfer_checked
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.system_program import SYS_PROGRAM_ID
import solana.system_program as system_program
import math


class PaymentTransactionBuilder:
    def __init__(self, rpc_client: Client):
        self._rpc_client = rpc_client

    def create(self, payer: PublicKey, payment_request: PaymentRequest) -> Transaction:
        raise NotImplementedError()

    def __create_transfer_instruction(self, payer: PublicKey, payment_request: PaymentRequest) -> TransactionInstruction:
        raise NotImplementedError() 

    def __create_memo_instruction(self, payment_request: PaymentRequest) -> TransactionInstruction:
        return TransactionInstruction(keys=[], program_id=MEMO_PROGRAM_ID, data=payment_request.memo.encode())

    def __add_reference_to_transfer_instruction(self, payment_request: PaymentRequest, transfer_instruction: TransactionInstruction):
        if payment_request.reference:
            if isinstance(payment_request.reference, list):
                for reference in payment_request.reference:
                    transfer_instruction.keys.append(
                        AccountMeta(reference, False, False))
            else:
                transfer_instruction.keys.append(
                    AccountMeta(reference, False, False))