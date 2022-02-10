from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from solana.publickey import PublicKey
from solana_pay.common.exceptions import CreatePaymentTransactionError
from solana_pay.common.utils.helpers import find_decimals
from solana_pay.common.consts import MEMO_PROGRAM_ID
from solana_pay.core.models import PaymentRequest
from solana_pay.core.payment_transaction_builder import PaymentTransactionBuilder
from solana.rpc.api import Client
from spl.token.client import Token
from spl.token.instructions import get_associated_token_address, transfer_checked
from spl.token.constants import TOKEN_PROGRAM_ID
import math


class SplPaymentTransactionBuilder(PaymentTransactionBuilder):
    def __init__(self, rpc_client: Client):
        super().__init__(rpc_client)

    def create(self, payer: PublicKey, payment_request: PaymentRequest) -> Transaction:
        transaction: Transaction = Transaction()
        transfer_instruction: TransactionInstruction = None
        transfer_instruction = self.__create_transfer_instruction(payer, payment_request)

        self.__add_reference_to_transfer_instruction(payment_request, transfer_instruction)
        
        if payment_request.memo:
            transaction.add(self.__create_memo_instruction(payment_request))

        transaction.add(transfer_instruction)

        return transaction

    @staticmethod
    def __validate_account_info_spl_token(account_info, account_info_name):
        if not account_info.is_initialized:
            raise CreatePaymentTransactionError(
                f"{account_info_name} not initialized.")
        elif account_info.is_frozen:
            raise CreatePaymentTransactionError(
                f"{account_info_name} is frozen.")

    def __create_transfer_instruction(self, payer: PublicKey, payment_request: PaymentRequest) -> TransactionInstruction:
        spl_client = Token(
            self._rpc_client, payment_request.spl_token, TOKEN_PROGRAM_ID, payer)
        mint = spl_client.get_mint_info()
        if not mint.is_initialized:
            raise CreatePaymentTransactionError("Mint not initialized.")

        if find_decimals(payment_request.amount) > mint.decimals:
            raise CreatePaymentTransactionError("Invalid amount of decimals.")

        payer_ata = get_associated_token_address(
            payer, payment_request.spl_token)
        payer_account_info = spl_client.get_account_info(payer_ata)
        SplPaymentTransactionBuilder.__validate_account_info_spl_token(
            payer_account_info, "Payer")

        recipient_ata = get_associated_token_address(
            payment_request.recipient, payment_request.spl_token)
        recipient_account_info = spl_client.get_account_info(recipient_ata)
        SplPaymentTransactionBuilder.__validate_account_info_spl_token(
            recipient_account_info, "Recipient")

        tokens = math.floor(payment_request.amount * (10 ** mint.decimals))
        if tokens > payer_account_info.amount:
            raise CreatePaymentTransactionError("Insufficient funds.")

        transfer_instruction = transfer_checked(amount=tokens, program_id=TOKEN_PROGRAM_ID,
                                                decimals=mint.decimals, owner=payer, source=payer_ata, dest=recipient_ata, mint=mint)

        return transfer_instruction
