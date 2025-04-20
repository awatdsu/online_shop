from typing import Literal

from pydantic import BaseModel, StrictStr, StrictBool, StrictInt, model_validator


class LoadConfig(BaseModel):
    cookie_key: StrictStr | None = "csrf-token"
    cookie_path: StrictStr | None = "/"
    cookie_domain: StrictStr | None = None
    cookie_samesite: Literal["lax", "none", "strict"] | None = "strict"
    cookie_secure: StrictBool | None = False
    header_name: StrictStr | None = "X-CSRF-Token"
    header_type: StrictStr | None = None
    httponly: StrictBool | None = True
    max_age: StrictInt | None = 3600
    secret_key: StrictStr | None = None
    token_location: Literal["body", "header"] | None = "header"
    salt: StrictStr | None = None
    # token_key: StrictStr | None = None

    @model_validator(mode="after")
    def validate_cookie_samesite_none_secure(self) -> "LoadConfig":
        if self.cookie_samesite in {None, "none"} and self.cookie_secure is not True:
            raise ValueError('The "cookie_secure" must be True if "cookie_samesite" set to "none".')
        return self

    # @model_validator(mode="after")
    # def validate_token_key(self) -> "LoadConfig":
    #     token_location: str = self.token_location if self.token_location is not None else "header"
    #     if token_location == "body":
    #         if self.token_key is None:
    #             raise ValueError('The "token_key" must be present when "token_location" is "body"')
    #     return self
    
__all__ = ("LoadConfig",)
