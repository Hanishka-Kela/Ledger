from src.infrastructure.database.session import SessionLocal
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.infrastructure.security.jwt import verify_access_token
from src.infrastructure.repositories.user_repository import UserRepository
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

security = HTTPBearer()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db:Session=Depends(get_db)):

    token = credentials.credentials

    try:
        user_id = verify_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials")

    user_repository = UserRepository(db)
    user = user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return user