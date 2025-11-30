import logging

from fastapi import FastAPI
from src.utils import load_routers


from src.users.router import router as users_router
from src.auth.router import router as auth_router 


log = logging.getLogger(__name__)

app = FastAPI(title="Booking System API")



load_routers(app) 


@app.get("/")
async def root():
    """Перевірка стану додатку."""
    return {"ok": True }