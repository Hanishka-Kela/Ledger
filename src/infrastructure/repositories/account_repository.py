from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.account import Account as DomainAccount
from src.infrastructure.database.account import Account as ORMAccount


class AccountRepository:

    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, account: ORMAccount) -> DomainAccount:
        return DomainAccount(
            account_id=account.account_id,
            owner_id=account.owner_id,
            name=account.name,
            type=account.type,
        )

    def get_by_id(self, account_id: UUID) -> DomainAccount | None:
        account = self.session.get(ORMAccount, account_id)

        if account is None:
            return None

        return self._to_domain(account)

    def get_by_owner_id(self, owner_id: UUID) -> list[DomainAccount]:
        accounts = self.session.scalars(
            select(ORMAccount).where(ORMAccount.owner_id == owner_id)
        ).all()

        return [self._to_domain(account) for account in accounts]