from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.infrastructure.database.entry import Entry

class EntryRepository:
    def __init__(self, session:Session):
        self.session = session

    def get_by_id(self, entry_id:UUID) -> Entry |None:
        return self.session.get(Entry, entry_id)

    def get_by_account_id(self, account_id:UUID)->list[Entry]:
        return self.session.scalars(select(Entry).where(Entry.account_id==account_id)).all()