from enum import Enum
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from src.domain.entry import Entry, EntryType

@dataclass
class Transaction:
    transaction_id:UUID
    timestamp:datetime
    description:str
    entries:list[Entry]

    def is_valid(self)->bool:
        net_balance = 0
        if len(self.entries)<2:
            raise ValueError("Transaction must contain at least 2 entries")
        else:
            for entry in self.entries:
                if entry.type == EntryType.DEBIT:
                    net_balance += entry.amount
                elif entry.type == EntryType.CREDIT:
                    net_balance -= entry.amount
        if net_balance == 0:
            return True
        else:
            return False
        
