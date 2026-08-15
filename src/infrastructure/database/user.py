from src.infrastructure.database.base import Base
import uuid
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String,UUID

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key = True)
    email: Mapped[str]= mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
