from sqlalchemy import Column, Float, String
from sqlalchemy.ext.declarative import declarative_base

from .database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    uuid = Column(String, primary_key=True, index=True, unique=True)
    balance = Column(Float, default=0.0)


class WalletError(Exception):
    pass
