from fastapi import Depends

from src.config import settings
from src.constants import DB_NAMING_CONVENTION
from sqlalchemy import (
    MetaData,
    Column,
    DateTime,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import as_declarative, declared_attr
from typing import Any

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI.unicode_string().replace('+asyncpg', '')

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


@as_declarative(metadata=metadata)
class Base:
    id: Any
    __name__: str
    __table_args__ = {'extend_existing': True}

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())


# Import all the models, so that Base has them before being
# imported by Alembic
from src.db.models import *  # noqa
