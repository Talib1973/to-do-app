"""Password hashing and verification using bcrypt."""
from passlib.context import CryptContext

# Configure Passlib CryptContext with bcrypt
# bcrypt is the recommended hashing algorithm for passwords
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Cost factor: 12 rounds is secure and performant
)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string (60 characters)

    Example:
        >>> hash = get_password_hash("mypassword123")
        >>> len(hash)
        60
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches hash, False otherwise

    Example:
        >>> hash = get_password_hash("mypassword123")
        >>> verify_password("mypassword123", hash)
        True
        >>> verify_password("wrongpassword", hash)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)
