from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    id: int
    balance: float
    
    class Config:
        from_attributes = True


class AccountWithUserResponse(AccountResponse):
    user_id: int
    user_email: str
    user_full_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    account_id: int
    user_id: int
    amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    is_admin: bool = False


class WebhookPayload(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: float
    signature: str
