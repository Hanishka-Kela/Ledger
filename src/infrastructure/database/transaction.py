from src.infrastructure.database.base import Base
import uuid
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String,UUID,DateTime
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.database.entry import Entry

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id:Mapped[uuid.UUID]= mapped_column(UUID, primary_key=True)
    timestamp:Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    description:Mapped[str]=mapped_column(String, nullable= False)
    entries: Mapped[list["Entry"]] = relationship(back_populates="transaction")