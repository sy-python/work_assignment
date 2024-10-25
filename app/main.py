import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db, engine
from .routes import router


@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
