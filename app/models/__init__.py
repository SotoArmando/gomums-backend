"""Pydantic models for request/response validation"""

from app.models.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfile,
    UserUpdate
)
from app.models.auth import (
    TokenResponse,
    AuthResponse,
    RefreshTokenRequest,
    GoogleAuthRequest
)
from app.models.challenge import (
    ChallengeBase,
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeGoalBase,
    ChallengeGoalCreate,
    ChallengeGoalResponse,
    UserChallengeBase,
    UserChallengeAssign,
    UserChallengeResponse,
    UserChallengeSimpleResponse,
    UserChallengeGoalResponse,
    ChallengeProgressUpdate
)

__all__ = [
    # User models
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserProfile",
    "UserUpdate",
    # Auth models
    "TokenResponse",
    "AuthResponse",
    "RefreshTokenRequest",
    "GoogleAuthRequest",
    # Challenge models
    "ChallengeBase",
    "ChallengeCreate",
    "ChallengeUpdate",
    "ChallengeResponse",
    "ChallengeGoalBase",
    "ChallengeGoalCreate",
    "ChallengeGoalResponse",
    "UserChallengeBase",
    "UserChallengeAssign",
    "UserChallengeResponse",
    "UserChallengeSimpleResponse",
    "UserChallengeGoalResponse",
    "ChallengeProgressUpdate",
]
