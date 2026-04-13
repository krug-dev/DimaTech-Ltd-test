import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Account, Payment
from app.schemas import WebhookPayload
from app.config import get_settings
from app.auth import get_current_admin

router = APIRouter(prefix="/api/webhook", tags=["webhook"])
settings = get_settings()


def verify_signature(payload: WebhookPayload) -> bool:
    data_string = f"{payload.account_id}{payload.amount}{payload.transaction_id}{payload.user_id}{settings.secret_key}"
    expected_signature = hashlib.sha256(data_string.encode()).hexdigest()
    return expected_signature == payload.signature


@router.post("/payment")
async def process_payment(
    payload: WebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    if not verify_signature(payload):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    result = await db.execute(select(User).filter(User.id == payload.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    payment_result = await db.execute(
        select(Payment).filter(Payment.transaction_id == payload.transaction_id)
    )
    existing_payment = payment_result.scalar_one_or_none()
    if existing_payment:
        return {"message": "Payment already processed", "status": "duplicate"}
    
    account_result = await db.execute(
        select(Account).filter(Account.id == payload.account_id, Account.user_id == payload.user_id)
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        account = Account(user_id=payload.user_id, balance=0.0)
        db.add(account)
        await db.commit()
        await db.refresh(account)
    
    payment = Payment(
        transaction_id=payload.transaction_id,
        account_id=account.id,
        user_id=payload.user_id,
        amount=payload.amount
    )
    db.add(payment)
    
    account.balance += payload.amount
    await db.commit()
    
    return {"message": "Payment processed successfully", "status": "success"}


@router.get("/payment/{transaction_id}")
async def get_payment(
    transaction_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Payment).filter(Payment.transaction_id == transaction_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
