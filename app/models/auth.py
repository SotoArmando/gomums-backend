from pydantic import BaseModel
from app.models.user import UserResponse


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds


class AuthResponse(BaseModel):
    """Schema for authentication response (includes user + tokens)"""
    user: UserResponse
    token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth authentication"""
    id_token: str
