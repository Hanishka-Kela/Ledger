from uuid import UUID
from src.infrastructure.database.transaction import Transaction
from src.infrastructure.database.entry import Entry
from sqlalchemy.orm import Session
from sqlalchemy import select

class TransactionRepository:
    def __init__(self,session:Session):
        self.session = session

    def get_by_id(self, transaction_id:UUID)->Transaction|None:
        return self.session.get(Transaction, transaction_id)

    def get_entries(self, transaction_id:UUID) -> list[Entry]:
        return self.session.scalars(select(Entry).where(Entry.transaction_id==transaction_id)).all()