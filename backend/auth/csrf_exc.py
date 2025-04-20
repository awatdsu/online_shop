

class CsrfProtectError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class InvalidHeaderError(CsrfProtectError):
    def __init__(self, message: str):
        super().__init__(422, message)


class MissingTokenError(CsrfProtectError):
    def __init__(self, message: str):
        super().__init__(400, message)


class TokenValidationError(CsrfProtectError):
    def __init__(self, message: str):
        super().__init__(401, message)


__all__ = ("CsrfProtectError", "InvalidHeaderError", "MissingTokenError", "TokenValidationError")
