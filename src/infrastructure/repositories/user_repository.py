from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.email == email)
        )

    def create(self, user: User) -> User:
        self.session.add(user)
        return user

    def exists_by_email(self, email: str) -> bool:
        return self.session.scalar(select(User.user_id).where(User.email == email))is not None