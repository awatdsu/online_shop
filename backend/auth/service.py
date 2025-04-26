from fastapi import Depends, HTTPException, Response, status

from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


from backend.auth.schemas import OkResponse, PasswordRecoveryConfirmRequest, PasswordRecoveryRequest, Token, UserResponseSchema, UserRegisterSchema
from backend.auth.tasks import send_confirm_email, send_passw_recovery_email
from backend.auth.utils import create_token, hash_password, verify_password
from backend.database.db import get_session
from backend.users.dao_users import UserDao

from backend.settings import settings

class AuthService:
    
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.user_dao = UserDao(session)


    async def login_for_access_token(self, *, username: str, password: str, response: Response) -> Token:
        user = await self.user_dao.find_one_or_none(username=username)

        if verify_password(plain_password=password, hashed_password=user.password) is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_token(data={"sub": user.username, "role": user.role}, expire_time_minutes=60*24)

        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite='lax')
        return Token(access_token=access_token, token_type="Bearer")
    
    async def register_new_user(self, *, user_data: UserRegisterSchema) -> UserResponseSchema:
        user_username = await self.user_dao.find_one_or_none(username=user_data.username)
        user_email = await self.user_dao.find_one_or_none(email=user_data.email)
        if user_username or user_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )

        user_dict = user_data.model_dump()
        user_dict["password"] = hash_password(user_data.password)
        user_dict.pop("repeat_password")

        await self.user_dao.add_user(**user_dict)

        try:
            await self.user_dao.session.commit()
        except SQLAlchemyError as e:
            await self.user_dao.session.rollback()
            print(f"SQLAlchemyError: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops.. Something unexpected happened"
            )
        
        serializer = URLSafeTimedSerializer(secret_key=settings.url_secret_keys.secret_key_url_reg.get_secret_value())
        confirm_token = serializer.dumps(user_dict["email"])
        await send_confirm_email(to_email=user_dict["email"], token=confirm_token)
        return UserResponseSchema(**user_dict)
        
    async def resend_verification_message(self, *, data: PasswordRecoveryRequest) -> OkResponse:
        user = await self.user_dao.find_one_or_none(email=data.email)
        if user is None:
            raise HTTPException(  
                status_code=404, detail=f"User with email {data.email} not found."  
            )
        
        if user.is_verificated:
            return OkResponse(status=f'{data.email} already verificated.')
        
        serializer = URLSafeTimedSerializer(secret_key=settings.url_secret_keys.secret_key_url_reg.get_secret_value())
        confirm_token = serializer.dumps(data.email)
        await send_confirm_email(to_email=data.email, token=confirm_token)

        return OkResponse()
    
    async def register_confirmation(self, *, token: str) -> OkResponse:
        serializer = URLSafeTimedSerializer(secret_key=settings.url_secret_keys.secret_key_url_reg.get_secret_value())
        try:
            email: str = serializer.loads(token, max_age=600)
        except BadSignature:
            raise HTTPException(  
                status_code=400, detail="Token is invalid or expired!"  
            )
        await self.user_dao.update_verification(email=email)

        try:
            await self.user_dao.session.commit()
        except SQLAlchemyError as e:
            await self.user_dao.session.rollback()
            print(f"SQLAlchemyError: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops.. Something unexpected happened"
            )
        return OkResponse()
    
    async def reset_password(self, *, data: PasswordRecoveryRequest) -> OkResponse:
        user = await self.user_dao.find_one_or_none(email=data.email)
        if user is None:
            raise HTTPException(  
                status_code=404, detail=f"User with email {data.email} not found."  
            )
        
        serializer = URLSafeTimedSerializer(secret_key=settings.url_secret_keys.secret_key_url_pwd.get_secret_value())
        password_recovery_token = serializer.dumps(data.email)
        await send_passw_recovery_email(to_email=data.email, token=password_recovery_token)
        return OkResponse()
    
    async def reset_password_confirm(self, *, token: str, passwords: PasswordRecoveryConfirmRequest) -> OkResponse:
        serializer = URLSafeTimedSerializer(secret_key=settings.url_secret_keys.secret_key_url_pwd.get_secret_value())
        try:
            email: str = serializer.loads(token, max_age=600)
        except BadSignature:  
            raise HTTPException(  
                status_code=400, detail="Token is invalid or expired!"  
            )
        
        new_passw_hash = hash_password(password=passwords.new_password)
        await self.user_dao.update_password(email=email, new_passw=new_passw_hash)

        try:
            await self.user_dao.session.commit()
        except SQLAlchemyError as e:
            await self.user_dao.session.rollback()
            print(f"SQLAlchemyError: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops.. Something unexpected happened"
            )
        return OkResponse()

