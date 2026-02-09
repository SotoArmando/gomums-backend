from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any

from app.models.auth import AuthResponse, RefreshTokenRequest, TokenResponse
from app.models.user import UserCreate, UserLogin, UserResponse
from app.db.repositories.user_repository import UserRepository
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_current_user_id
)


router = APIRouter()


# ==================== Register ====================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """
    Register a new user with email and password
    
    Request body:
    - name: User's full name
    - email: Valid email address
    - password: Password (minimum 6 characters)
    
    Returns:
    - User information and authentication tokens
    
    Raises:
    - 400: Email already registered
    - 422: Validation error (invalid email, weak password, etc.)
    """
    # Check if user already exists
    existing_user = UserRepository.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = UserRepository.create_user(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
        oauth_provider="email"
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Generate tokens
    token_data = {"sub": user["id"], "email": user["email"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Remove sensitive data from response
    user_response = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return AuthResponse(
        user=UserResponse(**user_response),
        token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


# ==================== Login ====================

@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin):
    """
    Authenticate user with email and password
    
    Request body:
    - email: User's email address
    - password: User's password
    
    Returns:
    - User information and authentication tokens
    
    Raises:
    - 401: Invalid credentials or inactive account
    """
    # Get user by email
    user = UserRepository.get_user_by_email(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is active
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    UserRepository.update_last_login(user["id"])
    
    # Generate tokens
    token_data = {"sub": user["id"], "email": user["email"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Remove sensitive data from response
    user_response = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return AuthResponse(
        user=UserResponse(**user_response),
        token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


# ==================== Refresh Token ====================

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    """
    Get a new access token using a refresh token
    
    Request body:
    - refresh_token: Valid refresh token
    
    Returns:
    - New access token and refresh token
    
    Raises:
    - 401: Invalid or expired refresh token
    """
    # Decode and verify refresh token
    try:
        payload = decode_token(request.refresh_token, "refresh")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify user still exists and is active
    user = UserRepository.get_user_by_id(user_id)
    if not user or not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    token_data = {"sub": user["id"], "email": user["email"]}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=86400  # 24 hours
    )


# ==================== Get Current User ====================

@router.get("/me", response_model=UserResponse)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user's information
    
    Requires: Bearer token in Authorization header
    
    Returns:
    - Current user's profile information
    
    Raises:
    - 401: Invalid or missing token
    - 404: User not found
    """
    user_id = current_user["id"]
    
    # Get fresh user data from database
    user = UserRepository.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)


# ==================== Logout ====================

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout current user
    
    Note: This is a placeholder endpoint. In a production app, you would:
    - Invalidate the refresh token in a token blacklist
    - Clear any server-side sessions
    
    For now, the client should simply discard the tokens.
    
    Requires: Bearer token in Authorization header
    
    Returns:
    - 204 No Content
    """
    # In a real implementation, you would:
    # 1. Add the refresh token to a blacklist table
    # 2. Clear any server-side sessions
    # For now, we just return success and let the client discard tokens
    
    return None


# ==================== Health Check for Auth ====================

@router.get("/health")
def auth_health_check():
    """
    Health check endpoint for authentication service
    """
    return {
        "status": "ok",
        "service": "authentication",
        "endpoints": [
            "POST /api/auth/register",
            "POST /api/auth/login",
            "POST /api/auth/refresh",
            "GET /api/auth/me",
            "POST /api/auth/logout"
        ]
    }
