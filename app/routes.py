from fastapi import APIRouter, Depends, HTTPException

from .database import get_db
from .services import (
    create_wallet,
    deposit,
    get_balance,
    get_wallet,
    withdraw,
)

router = APIRouter()


@router.post("/wallets/{wallet_uuid}/operation")
async def operation(wallet_uuid: str, operation: dict, db=Depends(get_db)):
    async with db as session:
        if not "operationType" in operation or not "amount" in operation:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        if operation["operationType"] == "DEPOSIT":
            await deposit(session, wallet_uuid, operation["amount"])
        elif operation["operationType"] == "WITHDRAW":
            await withdraw(session, wallet_uuid, operation["amount"])
        else:
            raise HTTPException(status_code=400, detail="Invalid operation type")
    return {"message": "Operation successful"}


@router.get("/wallets/{wallet_uuid}")
async def balance(wallet_uuid: str, db=Depends(get_db)):
    async with db as session:
        wallet = await get_wallet(session, wallet_uuid)
        return {"balance": wallet.balance}
