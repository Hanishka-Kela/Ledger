from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.domain.user import User as DomainUser

from src.api.schemas.auth import (
    SignUpRequest,
    SignUpResponse,
    LoginRequest,
    TokenResponse
)

from src.api.dependencies import (
    get_db,
    get_current_user
)

from src.application.auth_service import AuthService
from src.infrastructure.repositories.user_repository import UserRepository


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(
    request: SignUpRequest,
    db: Session = Depends(get_db)
):
    user_repository = UserRepository(db)

    service = AuthService(
        user_repository=user_repository
    )

    user = service.signup(
        email=request.email,
        password=request.password,
        confirm_password=request.confirm_password
    )

    db.commit()

    return SignUpResponse(
        user_id=user.user_id,
        email=user.email
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user_repository = UserRepository(db)

    service = AuthService(
        user_repository=user_repository
    )

    token = service.login(
        email=request.email,
        password=request.password
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=SignUpResponse
)
def get_me(
    user: DomainUser = Depends(get_current_user)
):
    return SignUpResponse(
        user_id=user.user_id,
        email=user.email
    )