from pydantic import BaseModel, EmailStr, Field

from app.schemas.users import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class ProfileUpdate(BaseModel):
    # role e is_active no se aceptan: un usuario no puede cambiarse el rol a sí mismo.
    # username y email son opcionales pero no admiten null.
    username: str = Field(None, min_length=3, max_length=50)
    email: EmailStr = None
    full_name: str | None = None


class ProfileUpdateResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
