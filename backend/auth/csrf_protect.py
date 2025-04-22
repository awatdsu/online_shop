"""
#CREATOR: https://github.com/aekasitt/fastapi-csrf-protect
"""
from hashlib import sha1
from os import urandom
from re import match
from typing import Literal, Tuple, Callable, Any, Sequence

from fastapi import Request, Response
from fastapi.datastructures import Headers

from pydantic import ValidationError
from pydantic_settings import BaseSettings

from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired

from backend.auth.csrf_exc import InvalidHeaderError, MissingTokenError, TokenValidationError
from backend.auth.csrf_config import LoadConfig


class CsrfConfig(object):
    _cookie_key: str = "csrf-token"
    _cookie_path: str = "/"
    _cookie_domain: str | None = None
    _cookie_samesite: Literal["lax", "strict", "none"] | None = None
    _cookie_secure: bool = False
    _header_name: str = "X-CSRF-Token"
    _header_type: str | None = None
    _httponly: bool = True
    _max_age: int = 3600
    _secret_key: str | None = None
    _token_location: str = "header"
    _salt: str = "csrf-salt"
    # _token_key: str = "csrf-token"

    @classmethod
    def load_config(cls, settings: Callable[..., Sequence[Tuple[str, Any]] | BaseSettings]) -> None:
        try:
            config = LoadConfig(**{key.lower(): value for key, value in settings()})
            cls._cookie_key = config.cookie_key or cls._cookie_key
            cls._cookie_path = config.cookie_path or cls._cookie_path
            cls._cookie_domain = config.cookie_domain
            cls._cookie_samesite = config.cookie_samesite
            cls._cookie_secure = False if config.cookie_secure is None else config.cookie_secure
            cls._header_name = config.header_name or cls._header_name
            cls._header_type = config.header_type
            cls._httponly = True if config.httponly is None else config.httponly
            cls._max_age = config.max_age or cls._max_age
            cls._secret_key = config.secret_key
            cls._token_location = config.token_location or cls._token_location
            cls._salt = config.salt or cls._salt
            # cls._token_key = config.token_key or cls._token_key

        except ValidationError:
            raise

        except Exception as err:
            print(err)
            raise TypeError('CsrfConfig must be pydantic "BaseSettings" or list of tuple')

class CsrfProtect(CsrfConfig):

    def generate_csrf_token(self, secret_key: str | None = None, salt: str | None = None) -> Tuple[str,str]:
        secret_key = secret_key or self._secret_key
        if secret_key is None:
            raise RuntimeError("A secret key must be provided to use CSRF protection")
        serializer = URLSafeTimedSerializer(secret_key=secret_key, salt=self._salt)
        token = sha1(urandom(64)).hexdigest()
        signed = serializer.dumps(token)
        return token, signed
    
    def get_csrf_from_headers(self, headers: Headers):
        header_name, header_type = self._header_name, self._header_type
        header_parts = None
        try:
            header_parts = headers[header_name].split()
        except KeyError:
            raise InvalidHeaderError(f'Bad headers. Expected "{header_name}" in headers')
        token = None
        if not header_type:
            # <HeaderName>: <Token>
            if len(header_parts) != 1:
                raise InvalidHeaderError(f'Bad {header_name} header. Expected value "<Token>"')
            token = header_parts[0]
        else:
        # <HeaderName>: <HeaderType> <Token>
            if not match(r"{}\s".format(header_type), headers[header_name]) or len(header_parts) != 2:
                raise InvalidHeaderError(
                f'Bad {header_name} header. Expected value "{header_type} <Token>"'
                )
            token = header_parts[1]
        return token
    
    def set_csrf_cookie(self, csrf_signed_token: str, response: Response):
        response.set_cookie(
            self._cookie_key,
            csrf_signed_token,
            max_age=self._max_age,
            path=self._cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=self._httponly,
            samesite=self._cookie_samesite,
        )

    def unset_csrf_cookie(self, response: Response) -> None:
        response.delete_cookie(
            self._cookie_key,
            path=self._cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=self._httponly,
            samesite=self._cookie_samesite,
        )
    
    async def validate_csrf(
        self, 
        request: Request, 
        cookie_key: str | None = None,
        secret_key: str | None = None,
        time_limit: int | None = None,
    ):
        secret_key = secret_key or self._secret_key
        if secret_key is None:
            raise RuntimeError("A secret key is required to use CsrfProtect extension.")
        
        cookie_key = cookie_key or self._cookie_key
        signed_token = request.cookies.get(cookie_key)
        if signed_token is None:
            raise MissingTokenError(f"Missing cookie: `{cookie_key}`.")
        
        time_limit = time_limit or self._max_age

        token: str
        if self._token_location == "header":
            token = self.get_csrf_from_headers(request.headers)
        else:
            raise InvalidHeaderError("The CSRF token must be provided in header.")
        
        serializer = URLSafeTimedSerializer(secret_key, salt=self._salt)
        try:
            signature: str = serializer.loads(signed_token, max_age=time_limit)
            if token != signature:
                if token != signature:
                    raise TokenValidationError("The CSRF signatures submitted do not match.")
        except SignatureExpired:
            raise TokenValidationError("The CSRF token has expired.")
        except BadData:
            raise TokenValidationError("The CSRF token is invalid.")

# class CsrfSettings(BaseSettings):
#     secret_key: str = "aboba"
#     cookie_samesite: str = "strict"
#     cookie_secure: bool = True
#     httponly: bool = True

# @CsrfProtect.load_config
# def get_csrf_config():
#     return CsrfSettings()

# csrf_protect = CsrfProtect()

# token1, token2 = csrf_protect.generate_csrf_token()
# print(token1, token2)

# for key,value in CsrfProtect.__dict__.items():
#     print(key, ":", value)