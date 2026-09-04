from pydantic import BaseModel
from uuid import UUID

from src.domain.account import AccountType

class CreateAccountRequest(BaseModel):
    name:str
    account_type:AccountType

class AccountResponse(BaseModel):
    account_id:UUID
    owner_id:UUID
    name:str
    type:AccountType

class BalanceResponse(BaseModel):
    account_id: UUID
    balance: int