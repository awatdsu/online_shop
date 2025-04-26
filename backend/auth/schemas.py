import re

from pydantic import BaseModel, Field, ConfigDict, EmailStr, ValidationInfo, field_validator


class UserRegisterSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(default=..., min_length=4, max_length=50, description="Username")
    email: EmailStr = Field(default=..., description="Email address")
    phone_number: str = Field(default=..., description="Phone number starting with '+'")
    first_name: str = Field(default=..., min_length=1, max_length=50, description="Name, 1 to 50 symbols")
    last_name: str = Field(default=..., min_length=1, max_length=50, description="Last name, 1 to 50 symbols")

    password: str = Field(...,min_length=8, max_length=50, description="Password, 8 to 50 symbols")
    repeat_password: str = Field(...,min_length=8, max_length=50, description="Repeat password")

    @field_validator('phone_number', mode='after')
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError("Phone number should start with '+', 1 to 15 symbols!")
        return value
    
    @field_validator('repeat_password', mode='after')
    @classmethod
    def check_password_match(cls, value:str, info: ValidationInfo) -> str:
        if value != info.data['password']:
            raise ValueError("Passwords do not match!")
        return value

class UsernameLoginSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(default=..., min_length=4, max_length=50, description="Username")
    password: str = Field(...,min_length=8, max_length=50, description="Password, 8 to 50 symbols")

class UserResponseSchema(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verificated: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

class PasswordRecoveryConfirmRequest(BaseModel):
    new_password: str
    new_password_repeat: str

    @field_validator('new_password_repeat', mode='after')
    @classmethod
    def check_password_match(cls, value:str, info: ValidationInfo) -> str:
        if value != info.data['new_password']:
            raise ValueError("Passwords do not match!")
        return value
    
class OkResponse(BaseModel):
    status: str = "OK"

class InvalidTokenResponse(BaseModel):
    status: str = "Token is invalid or expired!"

