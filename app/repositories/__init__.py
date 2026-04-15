from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models import User, Account, Payment
from app.exceptions import NotFoundException, ConflictException


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: str, full_name: str, is_admin: bool = False) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_admin=is_admin,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        await self.db.delete(user)


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, account_id: int) -> Optional[Account]:
        result = await self.db.execute(
            select(Account).options(selectinload(Account.user)).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[Account]:
        result = await self.db.execute(select(Account).where(Account.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user_id: int, initial_balance: float = 0.0) -> Account:
        account = Account(user_id=user_id, balance=initial_balance)
        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def update_balance(self, account_id: int, amount: float) -> Account:
        account = await self.get_by_id(account_id)
        if not account:
            raise NotFoundException("Account", account_id)
        account.balance += amount
        await self.db.flush()
        await self.db.refresh(account)
        return account


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        result = await self.db.execute(
            select(Payment).options(selectinload(Payment.account)).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        transaction_id: str,
        account_id: int,
        user_id: int,
        amount: float,
    ) -> Payment:
        payment = Payment(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
        )
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def get_by_user_id(self, user_id: int) -> List[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Payment]:
        result = await self.db.execute(
            select(Payment)
            .options(selectinload(Payment.account).selectinload(Account.user))
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())