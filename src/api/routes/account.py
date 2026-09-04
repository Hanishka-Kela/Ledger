from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas.account import AccountResponse, CreateAccountRequest
from src.api.dependencies import get_current_user, get_db

from src.application.account_service import AccountService
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.account_repository import AccountRepository

from src.domain.user import User as DomainUser


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"]
)


@router.post("", response_model=AccountResponse)
def create_account(
    request: CreateAccountRequest,
    current_user: DomainUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_repository = UserRepository(db)
    account_repository = AccountRepository(db)

    service = AccountService(
        user_repository=user_repository,
        account_repository=account_repository
    )

    account = service.create_account(
        user_id=current_user.user_id,
        name=request.name,
        account_type=request.account_type
    )

    db.commit()

    return AccountResponse(
        account_id=account.account_id,
        owner_id=account.owner_id,
        name=account.name,
        type=account.type
    )

@router.get("", response_model=list[AccountResponse])
def get_accounts(
    current_user:DomainUser = Depends(get_current_user),
    db: Session =Depends(get_db)
):
    user_repository = UserRepository(db)
    account_repository = AccountRepository(db)

    service = AccountService(
            user_repository=user_repository,
            account_repository=account_repository
    )

    accounts = service.get_user_accounts(current_user.user_id)

    return accounts

