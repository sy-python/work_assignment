from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Wallet


async def create_wallet(session: AsyncSession, uuid: str):
    wallet = Wallet(uuid=uuid)
    session.add(wallet)
    await session.commit()


async def get_wallet(session: AsyncSession, uuid: str, lock: bool = False) -> Wallet:
    if lock:
        wallet = select(Wallet).with_for_update().where(Wallet.uuid == uuid)
    else:
        wallet = select(Wallet).where(Wallet.uuid == uuid)
    wallet = (await session.execute(wallet)).scalars().first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


async def deposit(session: AsyncSession, uuid: str, amount: float):
    try:
        wallet = await get_wallet(session, uuid, lock=True)
    except HTTPException:
        await create_wallet(session, uuid)
        wallet = await get_wallet(session, uuid, lock=True)
    wallet.balance += amount
    await session.commit()


async def withdraw(session: AsyncSession, uuid: str, amount: float):
    wallet = await get_wallet(session, uuid, lock=True)
    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    wallet.balance -= amount
    await session.commit()


async def get_balance(session: AsyncSession, uuid: str) -> float:
    wallet = await get_wallet(session, uuid)
    return wallet.balance
