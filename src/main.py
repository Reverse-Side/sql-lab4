import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.utils import load_routers

log = logging.getLogger(__name__)

app = FastAPI(title="Ticket System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],  # фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_routers(app)


@app.get("/")
async def root():
    """Перевірка стану додатку."""
    return {"ok": True}
