from enum import Enum
from dataclasses import dataclass
from uuid import UUID
# from transacations import Transaction
# from accounts import Account

class EntryType(str,Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

@dataclass
class Entry:
    entry_id:UUID
    transaction_id:UUID
    account_id:UUID
    type:EntryType
    amount:int
