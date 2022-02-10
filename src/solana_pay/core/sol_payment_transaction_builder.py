from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from solana.publickey import PublicKey
from solana_pay.common.exceptions import CreatePaymentTransactionError
from solana_pay.common.utils.helpers import find_decimals
from solana_pay.common.consts import MEMO_PROGRAM_ID, SOL_DECIMALS, LAMPORTS_PER_SOL
from solana_pay.core.models import PaymentRequest
from solana_pay.core.payment_transaction_builder import PaymentTransactionBuilder
from solana.rpc.api import Client
from solana.system_program import SYS_PROGRAM_ID
import solana.system_program as system_program
import math



class SolPaymentTransactionBuilder(PaymentTransactionBuilder):
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
    def __validate_account_info_native_sol(account_info, account_info_name):
        if account_info["owner"] != SYS_PROGRAM_ID:
            raise CreatePaymentTransactionError(
                f"{account_info_name} owner is invalid.")
        elif account_info["executable"]:
            raise CreatePaymentTransactionError(
                f"{account_info_name} executable.")

    def __create_transfer_instruction(self, payer: PublicKey, payment_request: PaymentRequest) -> TransactionInstruction:
        payer_info = self._rpc_client.get_account_info(payer)[
            'result']["value"]
        if payer_info == None:
            raise CreatePaymentTransactionError(
                "Invalid payer pk was provided.")

        recipient_info = self._rpc_client.get_account_info(
            payment_request.recipient)['result']
        if recipient_info == None:
            raise CreatePaymentTransactionError(
                "Invaid recipient pk was provided.")

        SolPaymentTransactionBuilder.__validate_account_info_native_sol(
            payer_info, "Payer")
        SolPaymentTransactionBuilder.__validate_account_info_native_sol(
            recipient_info, "Recipient")

        if find_decimals(payment_request.amount) > SOL_DECIMALS:
            raise CreatePaymentTransactionError("Invalid amount of decimals.")

        amount_in_lamports = math.floor(
            payment_request.amount * LAMPORTS_PER_SOL)
        if amount_in_lamports > payer_info["lamports"]:
            raise CreatePaymentTransactionError("Insufficient funds.")

        transfer_instruction = system_program.transfer(
            from_pubkey=payer, to_pubkey=payment_request.recipient, lamports=amount_in_lamports)

        return transfer_instruction

