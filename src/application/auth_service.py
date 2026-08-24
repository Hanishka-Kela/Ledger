from uuid import uuid4

from src.domain.user import User as DomainUser
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.security.password import (hash_password, verify_password)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def signup(self,email: str,password: str,confirm_password: str) -> DomainUser:

        if password != confirm_password:
            raise ValueError("Passwords don't match")

        if self.user_repository.exists_by_email(email):
            raise ValueError("User already exists")
        
        password_hash = hash_password(password)

        user = DomainUser(user_id=uuid4(),email=email,password_hash=password_hash)

        self.user_repository.create(user)
        
        return user

    def login(self, email:str, password:str) ->str:
        user =  self.user_repository.get_by_email(email)

        if user is None :
            raise ValueError("Invalid Credentials")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid Credentials")
        