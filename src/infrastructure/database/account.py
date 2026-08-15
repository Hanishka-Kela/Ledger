from src.infrastructure.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import UUID, String, ForeignKey,Enum
import uuid
from src.domain.account import AccountType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.database.user import User


class Account(Base):
    __tablename__ = "accounts"
    account_id : Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    owner_id :Mapped[uuid.UUID]= mapped_column(UUID,ForeignKey("users.user_id"))
    name:Mapped[str]=mapped_column(String, nullable=False)
    type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    owner:Mapped["User"] = relationship(back_populates="accounts")