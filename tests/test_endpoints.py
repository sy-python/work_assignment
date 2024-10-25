import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.execute("DELETE FROM wallets;")
        await conn.execute("INSERT INTO wallets VALUES ('test_wallet', 150);")
        await conn.execute("INSERT INTO wallets VALUES ('empty', 0);")
        await conn.commit()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_deposit(client):
    response = client.post(
        "/wallets/test_wallet/operation",
        json={"operationType": "DEPOSIT", "amount": 10},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Operation successful"}


def test_withdraw(client):
    response = client.post(
        "/wallets/test_wallet/operation",
        json={"operationType": "WITHDRAW", "amount": 10},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Operation successful"}


def test_balance(client):
    response = client.get("/wallets/empty")
    assert response.status_code == 200
    assert response.json() == {"balance": 0.0}


def test_balance_change_deposit(client):
    response = client.get("/wallets/test_wallet")
    assert response.status_code == 200
    balance = response.json()["balance"]

    response = client.post(
        "/wallets/test_wallet/operation",
        json={"operationType": "DEPOSIT", "amount": 10},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Operation successful"}

    response = client.get("/wallets/test_wallet")
    assert response.status_code == 200
    assert response.json()["balance"] == balance + 10


def test_balance_change_withdraw(client):
    response = client.get("/wallets/test_wallet")
    assert response.status_code == 200
    balance = response.json()["balance"]

    response = client.post(
        "/wallets/test_wallet/operation",
        json={"operationType": "WITHDRAW", "amount": 10},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Operation successful"}

    response = client.get("/wallets/test_wallet")
    assert response.status_code == 200
    assert response.json()["balance"] == balance - 10


def test_insufficient_funds(client):
    response = client.post(
        "/wallets/empty/operation",
        json={"operationType": "WITHDRAW", "amount": 10},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Insufficient funds"}


def test_invalid_operation_type(client):
    response = client.post(
        "/wallets/empty/operation",
        json={"operationType": "INVALID", "amount": 10},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid operation type"}


def test_nonexistent_wallet(client):
    response = client.get("/wallets/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "Wallet not found"}


def test_invalid_json(client):
    response = client.post(
        "/wallets/empty/operation",
        json={"The Ultimate Question of Life, the Universe, and Everything": 42},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON format"}
