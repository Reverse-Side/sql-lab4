import logging

from fastapi import FastAPI

from src.utils import load_routers

log = logging.getLogger(__name__)

app = FastAPI(title="Booking System API")


load_routers(app)


@app.get("/")
async def root():
    """Перевірка стану додатку."""
    return {"ok": True}
