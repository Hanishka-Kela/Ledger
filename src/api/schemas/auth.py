from pydantic import (BaseModel, EmailStr)
from uuid import UUID

class SignUpRequest(BaseModel):
    email:EmailStr
    password: str
    confirm_password: str

class SignUpResponse(BaseModel):
    user_id:UUID
    email:EmailStr
    
class LoginRequest(BaseModel):
    email:EmailStr
    password:str

class TokenResponse(BaseModel):
    access_token:str
    token_type:str