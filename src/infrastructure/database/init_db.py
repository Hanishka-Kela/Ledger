from src.infrastructure.database.base import Base
from src.infrastructure.database.account import Account
from src.infrastructure.database.entry import Entry
from src.infrastructure.database.user import User
from src.infrastructure.database.transaction import Transaction
from src.infrastructure.database.engine import engine

Base.metadata.create_all(engine)