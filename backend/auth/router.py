from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestFormStrict

from pydantic_settings import BaseSettings

from backend.settings import settings
from backend.auth.csrf_protect import CsrfProtect
from backend.auth.dependencies import get_current_user
from backend.auth.schemas import InvalidTokenResponse, OkResponse, PasswordRecoveryConfirmRequest, PasswordRecoveryRequest, Token, UserResponseSchema, UserRegisterSchema
from backend.auth.service import AuthService

# from backend.auth.dao_tokens import UserTokenDao


router = APIRouter()

class CsrfSettings(BaseSettings):
    secret_key: str = settings.csrf_settings.secret_key_csrf.get_secret_value()
    cookie_samesite: str = "strict"
    cookie_secure: bool = True
    httponly: bool = True
    salt: str = settings.csrf_settings.salt_csrf.get_secret_value()

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()



@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    description="Endpoint for creating access token",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect username or password",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            }
        }
    }
)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()], service: Annotated[AuthService, Depends()], response: Response) -> Token:
    token = await service.login_for_access_token(username=form_data.username, password=form_data.password, response=response)
    return token


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    description="Endpoint for registration",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "User already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "User already exists"}
                }
            }
        }
    }
)
async def register_new_user(user_data: UserRegisterSchema, service: Annotated[AuthService, Depends()], request: Request) -> UserResponseSchema:
    response_data = await service.register_new_user(user_data=user_data)
    return response_data

@router.post(
    "/resend-email-verification",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse,
    description="Resend verification message",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User with email user@example.com not found"}
                }
            }
        }
    }
)
async def resend_verification_message(data: PasswordRecoveryRequest, service: Annotated[AuthService, Depends()]) -> OkResponse:
    response = await service.resend_verification_message(data=data)
    return response


@router.get(
    "/register-confirm",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse,
    description="Endpoint for registration confirmation",
    responses={
        status.HTTP_200_OK: {
            "model": OkResponse,
            "description": "Ok Response"
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": InvalidTokenResponse,
            "description": "Invalid token"
        }
    }
)
async def register_confirmation(token:str,  service: Annotated[AuthService, Depends()]) -> OkResponse:
    response = await service.register_confirmation(token=token)
    return response


@router.post(
    "/password-recovery",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse,
    description="Endpoint for password recovery",
    responses={
        status.HTTP_200_OK: {
            "model": OkResponse,
            "description": "Ok Response"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User with email user@example.com not found"}
                }
            }
        }
    }
)
async def reset_password(data: PasswordRecoveryRequest, service: Annotated[AuthService, Depends()]) -> OkResponse:
    response = await service.reset_password(data=data)
    return response


@router.post(
    "/password-recovery/confirm",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse,
    description="Endpoint for password recovery",
    responses={
        status.HTTP_200_OK: {
            "model": OkResponse,
            "description": "Ok Response"
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": InvalidTokenResponse,
            "description": "Invalid token"
        }
    }
)
async def reset_password_confirm(token: str, passwords: PasswordRecoveryConfirmRequest, service: Annotated[AuthService, Depends()]) -> OkResponse:
    response = await service.reset_password_confirm(token=token, passwords=passwords)
    return response


@router.get("/me")
async def get_me(current_user: Annotated[UserResponseSchema, Depends(get_current_user)], csrf_protect: Annotated[CsrfProtect, Depends()], response: Response):
    csrf_token, signed_token = csrf_protect.generate_csrf_token()
    print(signed_token, csrf_token)
    csrf_protect.set_csrf_cookie(signed_token, response)
    return {"aboba":"aboba"}

@router.post("/me")
async def post_me(current_user: Annotated[UserResponseSchema, Depends(get_current_user)], csrf_protect: Annotated[CsrfProtect, Depends()], request: Request, response: Response):
    await csrf_protect.validate_csrf(request)
    csrf_protect.unset_csrf_cookie(response)
    return {"aboba":"aboba"}
