from fastapi import FastAPI
from src.api.routes.auth import router as auth_router
from src.api.routes.account import router as account_router
from src.api.routes.transaction import router as transaction_router
import src.infrastructure.database

app = FastAPI()

app.include_router(auth_router)
app.include_router(account_router)
app.include_router(transaction_router)