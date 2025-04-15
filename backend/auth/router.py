import email
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.auth.schemas import Token, UserRegisterSchema
from backend.auth.utils import authenticate_user, create_access_token, hash_password
from backend.users.dao_users import UsersDao

router = APIRouter()


@router.post("/oauth/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register_new_user(user_data: UserRegisterSchema):
    user = await UsersDao.find_one_or_none(username=user_data.username, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    user_dict = user_data.model_dump()
    user_dict["password"] = hash_password(user_data.password)
    user_dict.pop("repeat_password")
    print(user_dict)
    #ДОБАВИТЬ ХЕШИРОВАНИЕ ПАРОЛЯ
    await UsersDao.add_new_user(**user_dict)
    return {'message': "Registration successfull"}