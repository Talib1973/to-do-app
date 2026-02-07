"""Authentication request and response schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator


class SignupRequest(BaseModel):
    """
    Request schema for user signup.

    Attributes:
        email: Valid email address
        password: Password (min 8 characters)
    """
    email: EmailStr = Field(
        ...,
        description="User email address",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        example="mypassword123"
    )

    @validator('password')
    def password_not_empty(cls, v):
        """Ensure password is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Password cannot be empty or whitespace')
        return v


class LoginRequest(BaseModel):
    """
    Request schema for user login.

    Attributes:
        email: Valid email address
        password: User password
    """
    email: EmailStr = Field(
        ...,
        description="User email address",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        description="User password",
        example="mypassword123"
    )


class TokenResponse(BaseModel):
    """
    Response schema for authentication endpoints.

    Returns JWT access token and user information.

    Attributes:
        access_token: JWT bearer token
        token_type: Always "bearer"
        user: User information
    """
    access_token: str = Field(
        ...,
        description="JWT access token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        example="bearer"
    )
    user: "UserResponse" = Field(
        ...,
        description="Authenticated user information"
    )


class UserResponse(BaseModel):
    """
    User information response schema.

    Attributes:
        id: User UUID
        email: User email address
        created_at: Account creation timestamp
    """
    id: UUID = Field(
        ...,
        description="User unique identifier",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    email: str = Field(
        ...,
        description="User email address",
        example="user@example.com"
    )
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        example="2026-02-06T10:00:00Z"
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Allow creating from SQLModel objects


# Update forward reference
TokenResponse.model_rebuild()
