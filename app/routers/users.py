from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from app.database import get_db
from app.models import User, Account
from app.schemas import UserResponse, AccountResponse, PaymentResponse, Token
from app.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["users"])
settings = get_settings()


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "is_admin": user.is_admin}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/accounts", response_model=list[AccountResponse])
async def get_my_accounts(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).filter(Account.user_id == current_user.id))
    accounts = result.scalars().all()
    return accounts


@router.get("/payments", response_model=list[PaymentResponse])
async def get_my_payments(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).filter(Account.user_id == current_user.id))
    accounts = result.scalars().all()
    account_ids = [acc.id for acc in accounts]
    
    if not account_ids:
        return []
    
    from sqlalchemy import select
    from app.models import Payment
    result = await db.execute(select(Payment).filter(Payment.account_id.in_(account_ids)))
    payments = result.scalars().all()
    return payments
