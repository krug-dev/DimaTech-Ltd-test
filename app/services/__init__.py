from typing import List, Optional
from passlib.context import CryptContext
from app.models import User, Account, Payment
from app.repositories import UserRepository, AccountRepository, PaymentRepository
from app.exceptions import NotFoundException, ConflictException, ValidationException
from app.schemas import UserCreate, UserUpdate, AccountCreate, PaymentCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, user_repo: UserRepository, account_repo: AccountRepository):
        self.user_repo = user_repo
        self.account_repo = account_repo

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repo.get_by_email(email)

    async def create_user(self, user_data: UserCreate) -> User:
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            raise ConflictException("Email already registered", field="email")

        hashed_password = pwd_context.hash(user_data.password)
        user = await self.user_repo.create(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_admin=user_data.is_admin if hasattr(user_data, 'is_admin') else False,
        )

        await self.account_repo.create(user_id=user.id, initial_balance=0.0)

        return user

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def delete_user(self, user_id: int) -> None:
        await self.user_repo.delete(user_id)


class AccountService:
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    async def get_account(self, account_id: int) -> Account:
        account = await self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundException("Account", account_id)
        return account

    async def get_user_account(self, user_id: int) -> Account:
        account = await self.account_repo.get_by_user_id(user_id)
        if not account:
            raise NotFoundException("Account for user", user_id)
        return account

    async def add_balance(self, account_id: int, amount: float) -> Account:
        if amount <= 0:
            raise ValidationException("Amount must be positive", field="amount")

        account = await self.account_repo.update_balance(account_id, amount)
        return account


class PaymentService:
    def __init__(self, payment_repo: PaymentRepository, account_repo: AccountRepository):
        self.payment_repo = payment_repo
        self.account_repo = account_repo

    async def create_payment(
        self,
        transaction_id: str,
        user_id: int,
        amount: float,
    ) -> Payment:
        existing = await self.payment_repo.get_by_transaction_id(transaction_id)
        if existing:
            raise ConflictException("Transaction already exists", field="transaction_id")

        account = await self.account_repo.get_by_user_id(user_id)
        if not account:
            raise NotFoundException("Account", account.id if hasattr(account, 'id') else 0)

        payment = await self.payment_repo.create(
            transaction_id=transaction_id,
            account_id=account.id,
            user_id=user_id,
            amount=amount,
        )

        await self.account_repo.update_balance(account.id, amount)

        return payment

    async def get_user_payments(self, user_id: int) -> List[Payment]:
        return await self.payment_repo.get_by_user_id(user_id)

    async def get_all_payments(self, limit: int = 100, offset: int = 0) -> List[Payment]:
        return await self.payment_repo.get_all(limit, offset)