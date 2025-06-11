# Purpose: Defines the Pydantic schemas related to authentication tokens.

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    Schema for the access token response.
    """
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """
    Schema for the data encoded within the JWT.
    The 'sub' (subject) field is standard for storing the user's identifier.
    """
    sub: Optional[str] = None