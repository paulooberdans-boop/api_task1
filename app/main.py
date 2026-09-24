from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_tables
from app.routes import router as tasks_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    yield


app = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)
app.include_router(tasks_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Report that the API process is available."""
    return {"status": "ok"}
