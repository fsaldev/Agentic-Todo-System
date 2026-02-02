from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.models.todo import Todo  # noqa: F401 — register model with Base
from app.routers.todos import router as todos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)
app.include_router(todos_router)
