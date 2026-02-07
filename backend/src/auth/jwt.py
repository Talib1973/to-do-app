"""JWT token generation and validation."""
import os
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is not set. "
        "This must be a random string of at least 32 characters."
    )

if len(SECRET_KEY) < 32:
    raise ValueError(
        f"BETTER_AUTH_SECRET must be at least 32 characters long. "
        f"Current length: {len(SECRET_KEY)}"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security scheme for FastAPI dependency injection
security = HTTPBearer()


def create_access_token(user_id: UUID, email: str) -> str:
    """
    Create a JWT access token for authenticated user.

    Args:
        user_id: User's UUID
        email: User's email address

    Returns:
        Encoded JWT token string

    Token Claims:
        - sub: User ID (subject)
        - email: User email
        - iat: Issued at timestamp
        - exp: Expiration timestamp (24 hours from now)

    Example:
        >>> token = create_access_token(
        ...     user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        ...     email="user@example.com"
        ... )
        >>> isinstance(token, str)
        True
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    payload = {
        "sub": str(user_id),  # Subject: user ID
        "email": email,
        "iat": now,  # Issued at
        "exp": expires_at,  # Expiration
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_current_user_id(
    credentials: HTTPAuthCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to extract and validate user_id from JWT token.

    This dependency should be used on all protected endpoints to:
    1. Verify the JWT signature
    2. Check token expiration
    3. Extract the user_id from the 'sub' claim

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User ID string extracted from JWT 'sub' claim

    Raises:
        HTTPException 401: If token is missing, invalid, or expired

    Usage:
        @app.get("/api/tasks")
        def list_tasks(user_id: str = Depends(get_current_user_id)):
            # user_id is guaranteed to be valid here
            return get_user_tasks(user_id)

    Example:
        >>> # With valid token
        >>> user_id = get_current_user_id(credentials)
        >>> isinstance(user_id, str)
        True
    """
    try:
        token = credentials.credentials

        # Decode and verify token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Extract user_id from 'sub' claim
        user_id: Optional[str] = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
