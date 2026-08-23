from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.infrastructure.database.account import Account


class AccountRepository:

    def __init__(self, session:Session):
        self.session = session

    def get_by_id(self, account_id :UUID) -> Account |None:
        return self.session.get(Account, account_id)

    def get_by_owner_id(self, owner_id:UUID) ->list[Account] :
        return self.session.scalars(select(Account).where(Account.owner_id==owner_id)).all()