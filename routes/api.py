from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth.jwt import (
    create_access_token,
    verify_password,
    get_current_user,
    get_password_hash
)
from app.config import get_settings

router = APIRouter()
settings = get_settings()

USER_DB = {
    "admin":{
        "username": "admin",
        "hashed_password": get_password_hash("test"),
        "user_id": 1
    }
}

@router.post("/health")
def health():
    return {"Message":"Health looks good!"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    user = USER_DB.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub":user["username"], "user_id":user["user_id"]},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """
    Requires valid JWT token in Authorization header.
    """
    return {
        "message": f"Hello {current_user['username']}",
        "user_id": current_user['user_id']
    }