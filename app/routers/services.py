from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories import UserRepository, AccountRepository, PaymentRepository
from app.services import UserService, AccountService, PaymentService
from app.exceptions import NotFoundException

router = APIRouter(prefix="/api", tags=["services"])


def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(UserRepository(db), AccountRepository(db))


def get_account_service(db: AsyncSession = Depends(get_db)):
    return AccountService(AccountRepository(db))


def get_payment_service(db: AsyncSession = Depends(get_db)):
    return PaymentService(PaymentRepository(db), AccountRepository(db))


async def get_current_user_id() -> int:
    return 1  # TODO: integrate with auth