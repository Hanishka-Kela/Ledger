from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.account import (
    AccountResponse,
    CreateAccountRequest,
    BalanceResponse
)

from src.api.dependencies import (
    get_current_user,
    get_db
)

from src.application.account_service import AccountService
from src.application.ledger_service import LedgerService

from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.transaction_repository import TransactionRepository
from src.infrastructure.repositories.entry_repository import EntryRepository

from src.domain.user import User as DomainUser


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"]
)


@router.post(
    "",
    response_model=AccountResponse
)
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


@router.get(
    "",
    response_model=list[AccountResponse]
)
def get_accounts(
    current_user: DomainUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_repository = UserRepository(db)
    account_repository = AccountRepository(db)

    service = AccountService(
        user_repository=user_repository,
        account_repository=account_repository
    )

    return service.get_user_accounts(
        current_user.user_id
    )


@router.get(
    "/{account_id}/balance",
    response_model=BalanceResponse
)
def get_account_balance(
    account_id: UUID,
    current_user: DomainUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account_repository = AccountRepository(db)
    transaction_repository = TransactionRepository(db)
    entry_repository = EntryRepository(db)

    ledger_service = LedgerService(
        account_repository=account_repository,
        transaction_repository=transaction_repository,
        entry_repository=entry_repository
    )

    try:
        balance = ledger_service.get_account_balance(
            requester_user_id=current_user.user_id,
            account_id=account_id
        )

        return BalanceResponse(
            account_id=account_id,
            balance=balance
        )

    except ValueError as exc:
        message = str(exc)

        if "does not exist" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )

        if "Not authorized" in message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )