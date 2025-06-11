from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class Msg(BaseModel):
    """Schema for generic messages."""
    msg: str

class ResetPassword(BaseModel):
    """Schema for the reset password request body."""
    token: str
    new_password: str

class TokenResponse(BaseModel):
    token: str

class RecoveryTokenResponse(BaseModel):
    token: str