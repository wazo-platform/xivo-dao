# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Index
from sqlalchemy.sql import Selectable
from sqlalchemy_utils import view

from .db_manager import Base, Session


def create_materialized_view(
    name: str, selectable: Selectable, indexes: list[Index] = None
):
    """
    Create a materialized view

    :param name (str): The name of the view to create.
    :param selectable (Selectable): An SQLAlchemy selectable e.g. a select() statement.
    :param indexes (list[Index]): An optional list of SQLAlchemy Index instances.
    """

    if not name:
        raise ValueError('view must have a name')

    if not isinstance(selectable, Selectable):
        raise ValueError('invalid view selectable, must be an SQLAlchemy Selectable')

    if indexes:
        for index in indexes:
            if not isinstance(index, Index):
                raise ValueError('invalid view index, must be an SQLAlchemy index')

    return view.create_materialized_view(name, selectable, Base.metadata, indexes)


class MaterializedView(Base):
    """
    Materialized View base class

    Used to tell SQLAlchemy to construct a materialized view.

    Usage:

        * Assign the `__table__` attribute using the `create_materialized_view` helper function
    """

    __abstract__: bool = True

    @classmethod
    def refresh(cls, concurrently: bool = True) -> None:
        view.refresh_materialized_view(Session(), cls.__table__.fullname, concurrently)
