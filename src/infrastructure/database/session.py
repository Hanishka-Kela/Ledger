from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.engine import engine

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False
)