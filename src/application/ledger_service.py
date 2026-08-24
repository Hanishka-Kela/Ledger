from uuid import UUID
from dataclasses import dataclass, field
from src.domain.entry import EntryType
from src.domain.transaction import Transaction
from src.infrastructure.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.transaction_repository import TransactionRepository
from src.infrastructure.repositories.entry_repository import EntryRepository

@dataclass
class LedgerService:
    pass