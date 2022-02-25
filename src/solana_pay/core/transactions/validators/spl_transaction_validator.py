from solana.transaction import TransactionSignature
from solana.publickey import PublicKey
from solana_pay.common.exceptions import ValidateTransactionError
from solana_pay.common.consts import LAMPORTS_PER_SOL
from solana.rpc.api import Client
from spl.token.instructions import get_associated_token_address
from solana.rpc.commitment import Commitment
from typing import Optional, Union, List, Dict
from solana_pay.core.transactions.validators.transaction_validator import TransactionDetails, TransactionValidator


class SplTransactionValidator(TransactionValidator):
    def __init__(self, rpc_client: Client):
        super().__init__(rpc_client)

    def __call__(self, transaction_details: TransactionDetails):
        transaction = self._rpc_client.get_transaction(
            transaction_details.signature, commitment=transaction_details.commitment).get("result")
        if transaction == None:
            raise ValidateTransactionError("Transaction was not found.")
        if transaction.get("meta") == None:
            raise ValidateTransactionError("Transaction has no meta.")
        if meta_error := transaction.get("meta").get("error"):
            ValidateTransactionError(meta_error)

        recipient_ata = get_associated_token_address(transaction_details.recipient, transaction_details.spl_token)

        if recipient_ata in transaction["transaction"]["message"]["accountKeys"]:
            recipient_ata_id = transaction["transaction"]["message"]["accountKeys"].index(
                recipient_ata)
            pre_balance = transaction["meta"]["preTokenBalances"][recipient_ata_id]
            post_balance = transaction["meta"]["postTOkenBalances"][recipient_ata_id]
        else:
            raise ValidateTransactionError("Recipient was not found.")

        pre_amount = pre_balance.get(
            "uiTokenAmount", {}).get("uiAmountString", 0)
        post_amount = post_balance.get(
            "uiTokenAmount", {}).get("uiAmountString", 0)

        SplTransactionValidator._validate_amount(
            pre_amount, post_amount, transaction_details.amount)
        SplTransactionValidator._validate_reference(
            transaction_details.reference, transaction["transaction"]["message"]["accountKeys"])

        return True
