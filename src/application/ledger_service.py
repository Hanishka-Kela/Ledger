from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.account import AccountType
from src.domain.entry import Entry, EntryType
from src.domain.transaction import Transaction

from src.infrastructure.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.transaction_repository import TransactionRepository
from src.infrastructure.repositories.entry_repository import EntryRepository


@dataclass(frozen=True)
class JournalEntryInput:
    account_id: UUID
    type: EntryType
    amount: int


class LedgerService:

    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        entry_repository: EntryRepository
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.entry_repository = entry_repository

    def _calculate_balance(self, account) -> int:
        entries = self.entry_repository.get_by_account_id(
            account.account_id
        )

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

    def _entry_type_for_change(
        self,
        account_type: AccountType,
        increase: bool
    ) -> EntryType:

        if account_type in (
            AccountType.ASSET,
            AccountType.EXPENSE
        ):
            return (
                EntryType.DEBIT
                if increase
                else EntryType.CREDIT
            )

        return (
            EntryType.CREDIT
            if increase
            else EntryType.DEBIT
        )

    def post_journal(
        self,
        requester_user_id: UUID,
        entries: list[JournalEntryInput],
        description: str
    ) -> Transaction:

        if len(entries) < 2:
            raise ValueError(
                "Journal transaction must contain at least two entries"
            )

        domain_entries = []

        transaction_id = uuid4()

        for entry_input in entries:

            account = self.account_repository.get_by_id(
                entry_input.account_id
            )

            if account is None:
                raise ValueError(
                    "Journal entry account does not exist"
                )

            if account.owner_id != requester_user_id:
                raise ValueError(
                    "Not authorized to use journal entry account"
                )

            if entry_input.amount <= 0:
                raise ValueError(
                    "Journal entry amount must be positive"
                )

            domain_entry = Entry(
                entry_id=uuid4(),
                transaction_id=transaction_id,
                account_id=entry_input.account_id,
                type=entry_input.type,
                amount=entry_input.amount
            )

            domain_entries.append(domain_entry)

        transaction = Transaction(
            transaction_id=transaction_id,
            timestamp=datetime.now(timezone.utc),
            description=description,
            entries=domain_entries
        )

        if not transaction.is_valid():
            raise ValueError(
                "Journal transaction is not balanced"
            )

        self.transaction_repository.create(
            transaction
        )

        for entry in domain_entries:
            self.entry_repository.create(
                entry
            )

        return transaction

    def post_transaction(
        self,
        requester_user_id: UUID,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: int,
        description: str
    ) -> Transaction:

        source_account = self.account_repository.get_by_id(
            source_account_id
        )

        if source_account is None:
            raise ValueError(
                "Source account does not exist"
            )

        if source_account.owner_id != requester_user_id:
            raise ValueError(
                "Not authorized to use source account"
            )

        destination_account = self.account_repository.get_by_id(
            destination_account_id
        )

        if destination_account is None:
            raise ValueError(
                "Destination account does not exist"
            )

        if amount <= 0:
            raise ValueError(
                "Amount must be positive"
            )

        source_balance = self._calculate_balance(
            source_account
        )

        if source_balance < amount:
            raise ValueError(
                "Insufficient funds"
            )

        source_entry_type = self._entry_type_for_change(
            source_account.type,
            increase=False
        )

        destination_entry_type = self._entry_type_for_change(
            destination_account.type,
            increase=True
        )

        if source_entry_type == destination_entry_type:
            raise ValueError(
                "Transaction would not produce one debit and one credit"
            )

        transaction_id = uuid4()

        source_entry = Entry(
            entry_id=uuid4(),
            transaction_id=transaction_id,
            account_id=source_account.account_id,
            type=source_entry_type,
            amount=amount
        )

        destination_entry = Entry(
            entry_id=uuid4(),
            transaction_id=transaction_id,
            account_id=destination_account.account_id,
            type=destination_entry_type,
            amount=amount
        )

        transaction = Transaction(
            transaction_id=transaction_id,
            timestamp=datetime.now(timezone.utc),
            description=description,
            entries=[
                source_entry,
                destination_entry
            ]
        )

        if not transaction.is_valid():
            raise ValueError(
                "Transaction is not balanced"
            )

        self.transaction_repository.create(
            transaction
        )

        self.entry_repository.create(
            source_entry
        )

        self.entry_repository.create(
            destination_entry
        )

        return transaction