"""Script to seed test data after migrations"""
import asyncio
from app.database import async_session_maker, engine, Base
from app.models import User, Account
from app.auth import get_password_hash


async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        user = User(
            id=1,
            email="user@test.com",
            hashed_password=get_password_hash("user123"),
            full_name="Test User",
            is_admin=False
        )
        admin = User(
            id=2,
            email="admin@test.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Test Admin",
            is_admin=True
        )
        account = Account(id=1, user_id=1, balance=0.0)
        
        session.add_all([user, admin, account])
        await session.commit()
        print("Test data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
