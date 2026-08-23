from uuid import UUID

from sqlalchemy.orm import Session

from src.infrastructure.database.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)