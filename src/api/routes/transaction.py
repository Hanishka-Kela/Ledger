from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas.transaction import CreateTransactionRequest, TransactionResponse, EntryResponse
from src.api.dependencies import get_db, get_current_user

from src.infrastructure.repositories.account_repository import AccountRepository
from src.infrastructure.repositories.transaction_repository import TransactionRepository
from src.infrastructure.repositories.entry_repository import EntryRepository

from src.application.ledger_service import LedgerService

from src.domain.user import User as DomainUser

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("",response_model=TransactionResponse)

def create_transaction(
    request:CreateTransactionRequest,
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
            requester_user_id = current_user.user_id,
            source_account_id=request.source_account_id,
            destination_account_id=request.destination_account_id,
            amount = request.amount,
            description=request.description
        )
        db.commit()
        return transaction
    
    except Exception:
        db.rollback()
        raise