from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models import User, Account
from app.schemas import UserResponse, UserCreate, UserUpdate, AccountWithUserResponse
from app.auth import get_current_admin, get_password_hash

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/me", response_model=UserResponse)
async def get_admin_me(current_admin: User = Depends(get_current_admin)):
    return current_admin


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    account = Account(user_id=new_user.id, balance=0.0)
    db.add(account)
    await db.commit()
    
    return new_user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.email:
        check_result = await db.execute(select(User).filter(User.email == user_data.email, User.id != user_id))
        if check_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_data.email
    
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/users", response_model=List[AccountWithUserResponse])
async def get_users_with_accounts(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Account, User)
        .join(User, Account.user_id == User.id)
        .filter(User.is_admin == False)
    )
    rows = result.all()
    
    accounts_with_users = []
    for account, user in rows:
        accounts_with_users.append({
            "id": account.id,
            "user_id": user.id,
            "balance": account.balance,
            "user_email": user.email,
            "user_full_name": user.full_name
        })
    
    return accounts_with_users
