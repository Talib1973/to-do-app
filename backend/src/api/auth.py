"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.database import get_session
from src.models.user import User
from src.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from src.auth.password import get_password_hash, verify_password
from src.auth.jwt import create_access_token, get_current_user_id

router = APIRouter()


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
    description="Register a new user with email and password. Returns JWT token on success."
)
def signup(
    request: SignupRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Create a new user account.

    - **email**: Valid email address (case-insensitive, must be unique)
    - **password**: Minimum 8 characters

    Returns JWT access token and user information.

    Raises:
        400: Email already registered or validation error
    """
    # Check if email already exists (case-insensitive)
    existing_user = session.exec(
        select(User).where(User.email.ilike(request.email))
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password with bcrypt
    password_hash = get_password_hash(request.password)

    # Create new user
    new_user = User(
        email=request.email.lower(),  # Store email in lowercase
        password_hash=password_hash
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(
        user_id=new_user.id,
        email=new_user.email
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            created_at=new_user.created_at
        )
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    description="Authenticate user and return JWT token."
)
def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Authenticate user with email and password.

    - **email**: User's email address
    - **password**: User's password

    Returns JWT access token and user information.

    Raises:
        401: Invalid credentials (email not found or password incorrect)
    """
    # Find user by email (case-insensitive)
    user = session.exec(
        select(User).where(User.email.ilike(request.email))
    ).first()

    # Return generic error message for security
    # Don't reveal whether email exists or password is wrong
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password hash
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token with 24-hour expiration
    access_token = create_access_token(
        user_id=user.id,
        email=user.email
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at
        )
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user information",
    description="Returns information about the authenticated user."
)
def get_current_user(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> UserResponse:
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.

    Returns user information (id, email, created_at).

    Raises:
        401: Invalid or missing JWT token
        404: User not found (should not happen with valid token)
    """
    from uuid import UUID

    user = session.get(User, UUID(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at
    )
