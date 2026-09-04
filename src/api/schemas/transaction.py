from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.domain.entry import EntryType


class CreateTransactionRequest(BaseModel):
    source_account_id: UUID
    destination_account_id: UUID
    amount: int
    description: str


class JournalEntryRequest(BaseModel):
    account_id: UUID
    type: EntryType
    amount: int


class CreateJournalTransactionRequest(BaseModel):
    description: str
    entries: list[JournalEntryRequest]


class EntryResponse(BaseModel):
    entry_id: UUID
    transaction_id: UUID
    account_id: UUID
    type: EntryType
    amount: int


class TransactionResponse(BaseModel):
    transaction_id: UUID
    timestamp: datetime
    description: str
    entries: list[EntryResponse]