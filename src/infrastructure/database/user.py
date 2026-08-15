from src.infrastructure.database.base import Base
import uuid
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String,UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.database.account import Account


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key = True)
    email: Mapped[str]= mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    accounts: Mapped[list["Account"]] = relationship(
        back_populates="owner"
    )