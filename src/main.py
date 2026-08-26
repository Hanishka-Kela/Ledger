from fastapi import FastAPI
from src.api.routes.auth import router as auth_router
import src.infrastructure.database

app = FastAPI()

app.include_router(auth_router)
