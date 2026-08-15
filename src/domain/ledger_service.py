from uuid import UUID
from dataclasses import dataclass, field
from src.domain.entry import EntryType
from domain.transactions import Transaction

@dataclass
class LedgerService:
    # In-memory storage acting as our temporary database
    transactions: list[Transaction] = field(default_factory=list)

    def post_transaction(self, transaction: Transaction) -> None:
        if not transaction.is_valid():
            raise ValueError("Transaction failed validation: debits do not equal credits.")
        self.transactions.append(transaction)

    def get_account_balance(self, account_id: UUID) -> int:
        net_balance = 0
        
        # 1. Loop through all posted transactions
        for transaction in self.transactions:
            # 2. Loop through all entries in each transaction
            for entry in transaction.entries:
                # 3. Only calculate for the target account
                if entry.account_id == account_id:
                    if entry.type == EntryType.DEBIT:
                        net_balance += entry.amount
                    elif entry.type == EntryType.CREDIT:
                        net_balance -= entry.amount
                        
        return net_balance
