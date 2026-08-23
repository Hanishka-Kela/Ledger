from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.transaction import Transaction as DomainTransaction
from src.domain.entry import Entry as DomainEntry

from src.infrastructure.database.transaction import Transaction as ORMTransaction
from src.infrastructure.database.entry import Entry as ORMEntry


class TransactionRepository:

    def __init__(self, session: Session):
        self.session = session

    def _to_domain_entry(self, entry: ORMEntry) -> DomainEntry:
        return DomainEntry(
            entry_id=entry.entry_id,
            transaction_id=entry.transaction_id,
            account_id=entry.account_id,
            type=entry.type,
            amount=entry.amount
        )

    def _to_domain_transaction(
        self,
        transaction: ORMTransaction
    ) -> DomainTransaction:

        entries = [
            self._to_domain_entry(entry)
            for entry in transaction.entries
        ]

        return DomainTransaction(
            transaction_id=transaction.transaction_id,
            timestamp=transaction.timestamp,
            description=transaction.description,
            entries=entries
        )

    def _to_orm_transaction(
        self,
        transaction: DomainTransaction
    ) -> ORMTransaction:

        return ORMTransaction(
            transaction_id=transaction.transaction_id,
            timestamp=transaction.timestamp,
            description=transaction.description
        )

    def get_by_id(
        self,
        transaction_id: UUID
    ) -> DomainTransaction | None:

        transaction = self.session.get(
            ORMTransaction,
            transaction_id
        )

        if transaction is None:
            return None

        return self._to_domain_transaction(transaction)

    def get_entries(
        self,
        transaction_id: UUID
    ) -> list[DomainEntry]:

        entries = self.session.scalars(
            select(ORMEntry).where(
                ORMEntry.transaction_id == transaction_id
            )
        ).all()

        return [
            self._to_domain_entry(entry)
            for entry in entries
        ]

    def create(
        self,
        transaction: DomainTransaction
    ) -> DomainTransaction:

        orm_transaction = self._to_orm_transaction(transaction)

        self.session.add(orm_transaction)

        return transaction