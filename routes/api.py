from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import timedelta
from app.auth.jwt import (
    create_access_token,
    verify_password,
    get_current_user,
    get_password_hash,
)
from app.utils.cache import (
    cache_response,
    invalidate_cache
)
from typing import Annotated
from app.config import get_settings
from app.routes.schemas import User

router = APIRouter()
settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

USER_DB = {
    "admin":{
        "username": "admin",
        "hashed_password": get_password_hash("test"),
        "user_id": 1
    }
}

TEST_USER_DB = {
    "USR1":{
        "username": "test_user1",
        "user_id": "USR1",
        "Address": "Test address 1",
        "Phone": 858686886868,
        "isActive": True
    },

    "USR2":{
        "username": "test_user2",
        "user_id": "USR2",
        "Address": "Test address 2",
        "Phone": 858686886867,
        "isActive": False
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

@router.get("/user/current_user")
async def current_user(current_user: dict = Depends(get_current_user)):
    """
    Requires valid JWT token in Authorization header.
    """
    return {
        "message": f"Hello {current_user['username']}",
        "user_id": current_user['user_id']
    }

@router.get('/user/{test_user_id}')
@limiter.limit("10/minute")
@cache_response(expire=60)
async def user_id(test_user_id:str, request: Request, current_user: dict = Depends(get_current_user)) -> dict:

    test_user = TEST_USER_DB.get(test_user_id, None)
    if not test_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not found, please enter the correct user id"
        )

    return test_user

@router.put('/user/{test_user_id}')
async def update_user(test_user_id:str, user_data:User , current_user: dict = Depends(get_current_user)):
    test_user = TEST_USER_DB.get(test_user_id, None)
    if not test_user:
        responses_content = {
            'status_code':status.HTTP_404_NOT_FOUND,
            'message':'User Not Found :('
        }
        return JSONResponse(content=responses_content, status_code=status.HTTP_404_NOT_FOUND)

    updated_test_user =  test_user | user_data.dict()
    TEST_USER_DB[test_user_id] = updated_test_user

    #Invalidate the cache
    invalidate_cache(pattern=f'user_id:*{test_user_id}*')

    responses_content = {
        'status_code':status.HTTP_200_OK,
        'data': updated_test_user,
        'message': 'Data updated successfully'
    }

    return JSONResponse(content=responses_content, status_code=status.HTTP_200_OK)
    