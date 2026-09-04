from uuid import UUID

from src.domain.entry import EntryType
from src.domain.transaction import Transaction
from src.domain.account import AccountType

from src.infrastructure.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.transaction_repository import TransactionRepository
from src.infrastructure.repositories.entry_repository import EntryRepository

class LedgerService:

    def __init__(
            self, 
            account_repository:AccountRepository, 
            transaction_repository:TransactionRepository,
            entry_repository:EntryRepository
):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.entry_repository = entry_repository

    def _calculate_balance(self, account) -> int:
        entries = self.entry_repository.get_by_account_id(account.account_id)

        total_debits = 0
        total_credits = 0

        for entry in entries:
            if entry.type == EntryType.DEBIT:
                total_debits += entry.amount
            elif entry.type == EntryType.CREDIT:
                total_credits += entry.amount

        if account.type in (
            AccountType.ASSET,
            AccountType.EXPENSE
        ):
            return total_debits - total_credits

        return total_credits - total_debits

    def _entry_type_for_change(self, account_type: AccountType, increase: bool) -> EntryType:
        if account_type in (
            AccountType.ASSET,
            AccountType.EXPENSE
        ):
            return EntryType.DEBIT if increase else EntryType.CREDIT
        return EntryType.CREDIT if increase else EntryType.DEBIT

    def post_transaction(
    self,
    requester_user_id: UUID,
    source_account_id: UUID,
    destination_account_id: UUID,
    amount: int,
    description: str
) -> Transaction:

        source_account = self.account_repository.get_by_id(source_account_id)

        if source_account is None:
            raise ValueError("Source account does not exist")

        if source_account.owner_id != requester_user_id:
            raise ValueError("Not authorized to use source account")

        destination_account = self.account_repository.get_by_id(
            destination_account_id
        )

        if destination_account is None:
            raise ValueError("Destination account does not exist")

        if amount <= 0 :
            raise ValueError("Amount must be positive")

        source_balance = self._calculate_balance(source_account)

        if source_balance< amount :
            raise ValueError("Insufficient funds")
        