from uuid import uuid4

from src.application.account_service import AccountService

from src.domain.account import Account as DomainAccount
from src.domain.account import AccountType
from src.domain.user import User as DomainUser

from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.account_repository import AccountRepository


def test_get_user_accounts(db_session):
    user_id = uuid4()
    account_1_id = uuid4()
    account_2_id = uuid4()

    user = DomainUser(
        user_id=user_id,
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password"
    )

    account_1 = DomainAccount(
        account_id=account_1_id,
        owner_id=user_id,
        name="Savings Account",
        type=AccountType.ASSET
    )

    account_2 = DomainAccount(
        account_id=account_2_id,
        owner_id=user_id,
        name="Checking Account",
        type=AccountType.ASSET
    )

    user_repository = UserRepository(db_session)
    account_repository = AccountRepository(db_session)

    # Persist using the ORM repositories/database setup
    # This test will need ORM objects because the repositories
    # currently read from the database.