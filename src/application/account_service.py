from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.account_repository import AccountRepository
from src.domain.user import User as DomainUser
from src.domain.account import Account as DomainAccount
from uuid import UUID

class AccountService:

    def __init__(self, user_repository:UserRepository, account_repository:AccountRepository):
        self.user_repository=user_repository
        self.account_repository = account_repository

    def get_user_accounts(self, user_id:UUID) -> list[DomainAccount]:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError("User not Found")
        
        return self.account_repository.get_by_owner_id(user_id)