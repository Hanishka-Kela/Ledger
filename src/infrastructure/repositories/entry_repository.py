from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.entry import Entry as DomainEntry

from src.infrastructure.database.entry import Entry as ORMEntry


class EntryRepository:

    def __init__(self, session: Session):
        self.session = session

    def _to_domain(
        self,
        entry: ORMEntry
    ) -> DomainEntry:

        return DomainEntry(
            entry_id=entry.entry_id,
            transaction_id=entry.transaction_id,
            account_id=entry.account_id,
            type=entry.type,
            amount=entry.amount
        )

    def _to_orm(
        self,
        entry: DomainEntry
    ) -> ORMEntry:

        return ORMEntry(
            entry_id=entry.entry_id,
            transaction_id=entry.transaction_id,
            account_id=entry.account_id,
            type=entry.type,
            amount=entry.amount
        )

    def get_by_id(
        self,
        entry_id: UUID
    ) -> DomainEntry | None:

        entry = self.session.get(
            ORMEntry,
            entry_id
        )

        if entry is None:
            return None

        return self._to_domain(entry)

    def get_by_account_id(
        self,
        account_id: UUID
    ) -> list[DomainEntry]:

        entries = self.session.scalars(
            select(ORMEntry).where(
                ORMEntry.account_id == account_id
            )
        ).all()

        return [
            self._to_domain(entry)
            for entry in entries
        ]

    def create(
        self,
        entry: DomainEntry
    ) -> DomainEntry:

        orm_entry = self._to_orm(entry)

        self.session.add(orm_entry)

        return entry