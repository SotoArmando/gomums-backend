from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()


# ==================== Password Hashing ====================

def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT Token Generation ====================

def parse_expiration(expires_in: str) -> timedelta:
    """
    Parse expiration string like '24h', '7d', '30m' into timedelta
    
    Args:
        expires_in: String like '24h', '7d', '30m'
    
    Returns:
        timedelta object
    """
    unit = expires_in[-1]
    value = int(expires_in[:-1])
    
    if unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 's':
        return timedelta(seconds=value)
    else:
        return timedelta(hours=24)  # Default to 24 hours


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing token payload (typically user_id)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + parse_expiration(settings.JWT_EXPIRES_IN)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Dictionary containing token payload (typically user_id)
    
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + parse_expiration(settings.REFRESH_TOKEN_EXPIRES_IN)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.REFRESH_TOKEN_SECRET,
        algorithm="HS256"
    )
    
    return encoded_jwt


def decode_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token string
        token_type: Type of token ('access' or 'refresh')
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        secret = settings.JWT_SECRET if token_type == "access" else settings.REFRESH_TOKEN_SECRET
        
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"]
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}"
            )
        
        return payload
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ==================== Authentication Dependency ====================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get the current authenticated user from JWT token
    
    Usage in routes:
        @app.get("/protected")
        def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user["sub"]
            ...
    
    Args:
        credentials: HTTP Bearer token from request header
    
    Returns:
        Dictionary containing user information from token payload
    
    Raises:
        HTTPException: If token is invalid or missing required fields
    """
    token = credentials.credentials
    payload = decode_token(token, "access")
    
    # Extract user ID from payload
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID (sub claim)"
        )
    
    return {
        "id": user_id,
        **payload
    }


def get_current_user_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Convenience dependency to get just the user ID
    
    Usage in routes:
        @app.get("/profile")
        def get_profile(user_id: str = Depends(get_current_user_id)):
            ...
    """
    return current_user["id"]
