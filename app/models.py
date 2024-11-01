from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from .database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    uuid = Column(String, primary_key=True, index=True, unique=True)
    balance = Column(Integer, default=0)


class WalletError(Exception):
    pass
