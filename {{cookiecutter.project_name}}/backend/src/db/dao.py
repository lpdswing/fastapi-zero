from typing import List, Optional, TypeVar, Generic

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement
from src.db.deps import get_db_session
from src.db.base import Base

T = TypeVar("T", bound=Base)
DummyModel: T

__all__ = ["DAO"]


class DAO:
    """Class for accessing dummy table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_dummy_model(self, **kwargs) -> None:
        """
        Add single dummy to session.
        """
        self.session.add(DummyModel(**kwargs))  # noqa

    async def get_all_dummies(self, limit: int, offset: int) -> List[DummyModel]:
        """
        Get all dummy models with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: stream of dummies.
        """
        raw_dummies = await self.session.execute(
            select(DummyModel).limit(limit).offset(offset),
        )

        return list(raw_dummies.scalars().fetchall())

    async def filter(
            self,
            **kwargs
    ) -> List[DummyModel]:
        """
        Get specific dummy model.

        :return: dummy models.
        """
        query = select(DummyModel)
        for k, v in kwargs.items():
            column: ColumnElement = getattr(DummyModel, k, None)
            if column is not None:
                query = query.where(column == v)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
