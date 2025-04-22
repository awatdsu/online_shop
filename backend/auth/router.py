import os

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestFormStrict
from itsdangerous import BadSignature, URLSafeTimedSerializer
from pydantic_settings import BaseSettings

from backend.auth.csrf_protect import CsrfProtect
from backend.auth.dependencies import get_current_user
from backend.auth.schemas import PasswordRecoveryConfirmRequest, PasswordRecoveryRequest, Token, UserRegResponseSchema, UserRegisterSchema
from backend.auth.tasks import send_confirm_email, send_passw_recovery_email
from backend.auth.utils import authenticate_user, create_token, generate_fingerprint, hash_password
from backend.users.dao_users import UsersDao
# from backend.auth.dao_tokens import UserTokenDao


router = APIRouter()

class CsrfSettings(BaseSettings):
    secret_key: str = os.getenv("SECRET_KEY_CSRF")
    cookie_samesite: str = "strict"
    cookie_secure: bool = True
    httponly: bool = True
    salt: str = os.getenv("SALT_CSRF")

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()



@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()], response: Response, request: Request) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    fingerprint = generate_fingerprint(request)
    access_token = create_token(data={"sub": user.username, "device": fingerprint}, expire_time_minutes=60*24)
    # refresh_token= create_token(data={"sub": user.username, "device": fingerprint}, expire_time_minutes=60*24*3)

    # await UserTokenDao.refresh_user_token(user_id=user.id, new_token=refresh_token)
    # await UserTokenDao.set_device_to_user_data(user_id=user.id, new_device=fingerprint)

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite='lax')
    # response.set_cookie(key="refresh_token", value=refresh_token, secure=True, samesite='strict')

    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register_new_user(user_data: UserRegisterSchema, request: Request):
    user = await UsersDao.find_one_or_none(username=user_data.username, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    user_dict = user_data.model_dump()
    user_dict["password"] = hash_password(user_data.password)
    user_dict.pop("repeat_password")

    await UsersDao.add_new_user(**user_dict)
    
    serializer = URLSafeTimedSerializer(secret_key=os.getenv("SECRET_KEY_CSRF"))
    confirm_token = serializer.dumps(user_dict["email"])
    await send_confirm_email(to_email=user_dict["email"], token=confirm_token)
    # fingerprint = generate_fingerprint(request)
    # await UserTokenDao.add_new_user_token_data(
    #     refresh_token=create_token(data={"sub": user_data.username, "device": fingerprint}, expire_time_minutes=60*24*3),
    #     devices=[fingerprint],
    #     user_id=user_id
    # )

    return {'message': "Registration successfull"}


@router.get("/register-confirm")
async def register_confirmation(token:str):
    serializer = URLSafeTimedSerializer(secret_key=os.getenv("SECRET_KEY_CSRF"))
    try:
        email: str = serializer.loads(token, max_age=3600)
    except BadSignature:  
        raise HTTPException(  
            status_code=400, detail="Неверный или просроченный токен"  
        )
    await UsersDao.update_verification(email=email)
    return {'message': 'Verification successfull'}


@router.post("/password-recovery")
async def reset_password(data: PasswordRecoveryRequest):
    serializer = URLSafeTimedSerializer(secret_key=os.getenv("SECRET_KEY_CSRF"))
    password_recovery_token = serializer.dumps(data.email)
    await send_passw_recovery_email(to_email=data.email, token=password_recovery_token)
    
@router.post("/password-recovery-confirm")
async def password_recovery_confirm(token: str, passwords=PasswordRecoveryConfirmRequest):
    serializer = URLSafeTimedSerializer(secret_key=os.getenv("SECRET_KEY_CSRF"))
    try:
        email: str = serializer.loads(token, max_age=900)
    except BadSignature:  
        raise HTTPException(  
            status_code=400, detail="Неверный или просроченный токен"  
        )
    new_passw_hash = hash_password(password=passwords.new_password)
    await UsersDao.update_password(email=email, new_passw=new_passw_hash)
    return
    


# @router.post("/oauth/refresh")
# async def refresh_user_token(token: Annotated[str, Depends(oauth2_scheme)], response: Response, request: Request) -> Token:

#     user = await authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     fingerprint = generate_fingerprint(request)
#     access_token = create_token(data={"sub": user.username, "device": fingerprint}, expire_time_minutes=60)
#     refresh_token= create_token(data={"sub": user.username, "device": fingerprint}, expire_time_minutes=60*24*3)

#     await UserTokenDao.refresh_user_token(user_id=user.id, new_token=refresh_token)
#     await UserTokenDao.set_device_to_user_data(user_id=user.id, new_device=fingerprint)

#     response.set_cookie(key="access_token", value=access_token, secure=True, samesite='lax')
#     response.set_cookie(key="refresh_token", value=refresh_token, secure=True, samesite='strict')

#     return Token(access_token=access_token, token_type="bearer")

@router.get("/me")
async def get_me(current_user: Annotated[UserRegResponseSchema, Depends(get_current_user)], csrf_protect: Annotated[CsrfProtect, Depends()], response: Response):
    csrf_token, signed_token = csrf_protect.generate_csrf_token()
    print(signed_token, csrf_token)
    csrf_protect.set_csrf_cookie(signed_token, response)
    return {"aboba":"aboba"}

@router.post("/me")
async def post_me(current_user: Annotated[UserRegResponseSchema, Depends(get_current_user)], csrf_protect: Annotated[CsrfProtect, Depends()], request: Request, response: Response):
    await csrf_protect.validate_csrf(request)
    csrf_protect.unset_csrf_cookie(response)
    return {"aboba":"aboba"}
