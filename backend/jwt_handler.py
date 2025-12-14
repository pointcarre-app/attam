"""
JWT token handling for authentication.
Provides functions to create and verify JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from backend.settings import SECRET_KEY

# JWT Configuration
# TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 48


def create_access_token(access_name: str, expires_delta: timedelta) -> str:
    """
    Create a JWT token for the given access_name.

    Args:
        access_name: The user's access name to encode in the token
        expires_delta: Time until token expiration

    Returns:
        Encoded JWT token string
    """
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": access_name,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return access_name if valid.

    Args:
        token: The JWT token string to verify

    Returns:
        The access_name if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        access_name: str = payload.get("sub")
        if access_name is None:
            return None
        return access_name
    except JWTError:
        return None
