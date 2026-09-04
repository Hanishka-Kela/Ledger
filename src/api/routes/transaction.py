from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import (
    get_db,
    get_current_user
)

from src.api.schemas.transaction import (
    CreateTransactionRequest,
    CreateJournalTransactionRequest,
    TransactionResponse
)

from src.application.ledger_service import (
    JournalEntryInput,
    LedgerService
)

from src.infrastructure.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.transaction_repository import TransactionRepository
from src.infrastructure.repositories.entry_repository import EntryRepository

from src.domain.user import User as DomainUser


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


def _raise_http_error(exc: ValueError):
    message = str(exc)

    if "Not authorized" in message:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )

    if "does not exist" in message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )


@router.post(
    "",
    response_model=TransactionResponse
)
def create_transaction(
    request: CreateTransactionRequest,
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
        transaction = ledger_service.post_transaction(
            requester_user_id=current_user.user_id,
            source_account_id=request.source_account_id,
            destination_account_id=request.destination_account_id,
            amount=request.amount,
            description=request.description
        )

        db.commit()

        return transaction

    except ValueError as exc:
        db.rollback()
        _raise_http_error(exc)

    except Exception:
        db.rollback()
        raise


@router.post(
    "/journal",
    response_model=TransactionResponse
)
def create_journal_transaction(
    request: CreateJournalTransactionRequest,
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

    journal_entries = [
        JournalEntryInput(
            account_id=entry.account_id,
            type=entry.type,
            amount=entry.amount
        )
        for entry in request.entries
    ]

    try:
        transaction = ledger_service.post_journal(
            requester_user_id=current_user.user_id,
            entries=journal_entries,
            description=request.description
        )

        db.commit()

        return transaction

    except ValueError as exc:
        db.rollback()
        _raise_http_error(exc)

    except Exception:
        db.rollback()
        raise