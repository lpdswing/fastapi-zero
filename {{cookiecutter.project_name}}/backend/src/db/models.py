from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from src.db.base import Base
from fastapi_users.db import SQLAlchemyBaseUserTable

__all__ = ["User"]


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
