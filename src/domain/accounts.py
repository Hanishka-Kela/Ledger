from enum import Enum
from dataclasses import dataclass
from uuid import UUID

class AccountType(str,Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"

@dataclass
class Account:
    account_id:UUID
    owner_id:UUID
    name:str
    type:AccountType