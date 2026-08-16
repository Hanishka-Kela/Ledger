from src.infrastructure.database.base import Base
from sqlalchemy.orm import mapped_column, Mapped,relationship
from sqlalchemy import Integer, UUID,Enum,ForeignKey
from src.domain.entry import EntryType
import uuid
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.infrastructure.database.transaction import Transaction
    from src.infrastructure.database.account import Account

class Entry(Base):
    __tablename__ = "entries"
    entry_id:Mapped[uuid.UUID] = mapped_column(UUID,primary_key=True)
    transaction_id:Mapped[uuid.UUID] = mapped_column(UUID,ForeignKey("transactions.transaction_id"))
    account_id:Mapped[uuid.UUID] = mapped_column(UUID,ForeignKey("accounts.account_id"),index=True)
    type:Mapped[EntryType] = mapped_column(Enum(EntryType))
    amount:Mapped[int] = mapped_column(Integer)
    transaction:Mapped["Transaction"] = relationship(back_populates="entries")
    account:Mapped["Account"]= relationship(back_populates="entries")