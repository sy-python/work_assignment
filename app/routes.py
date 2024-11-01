from fastapi import APIRouter, Depends, HTTPException

from .database import get_db
from .models import WalletError
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
            try:
                await withdraw(session, wallet_uuid, operation["amount"])
            except WalletError as e:
                if e.args[0] == "Insufficient funds":
                    raise HTTPException(status_code=400, detail=e.args[0])
                elif e.args[0] == "Wallet not found":
                    raise HTTPException(status_code=404, detail=e.args[0])
                else:
                    raise HTTPException(status_code=500, detail=e.args[0])
        else:
            raise HTTPException(status_code=400, detail="Invalid operation type")
    return {"message": "Operation successful"}


@router.get("/wallets/{wallet_uuid}")
async def balance(wallet_uuid: str, db=Depends(get_db)):
    async with db as session:
        wallet = await get_wallet(session, wallet_uuid)
        return {"balance": wallet.balance}
