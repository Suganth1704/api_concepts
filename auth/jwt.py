from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import get_settings


settings = get_settings()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

def verify_password(plain_password:str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta:Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional custom expiration time
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiration and issued-at claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })

    encode_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encode_jwt

def decode_access_token(token:str) -> dict:
    """
    Decode and validate a JWT token.

    Rasie:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithm=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status=status.HTTP_401_UNAUTHORIZED,
            details="Could not validate credntials",
            headers={"WWW-Authenticate":"Bearer"}
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency to extract and validate the current user from JWT token.
    use this in the rout dependencies to protect endpoints.
    """
    payload = decode_access_token(token)
    username: str = payload.get("sub")

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return {"username": username, "user_id": payload.get("user_id")}