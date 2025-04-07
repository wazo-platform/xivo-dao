# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import Table
from sqlalchemy.event import contains, listens_for
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.unitofwork import UOWTransaction
from sqlalchemy_utils.view import refresh_materialized_view

from .db_manager import Base, Session


class MaterializedView(Base):
    """
    Materialized View base class

    Used to tell SQLAlchemy to construct a materialized view.

    Usage:

    Assign the '__table__' attribute using the create_materialized_view function
    """

    __abstract__ = True
    __view_dependencies__: tuple[type[Base], ...] = tuple()
    _view_dependencies_handler: Callable[[Session, str, bool], None] | None

    def __init_subclass__(cls) -> None:
        if not isinstance(getattr(cls, '__table__', None), Table):
            raise InvalidRequestError(
                f"Class '{cls}' '__table__' attribute must be created with 'create_materialized_view'"
            )
        super().__init_subclass__()
        _custom_dirty_attr = f'_wazo_{cls.__table__}_has_been_flushed_being_dirty'

        if targets := cls.__view_dependencies__:

            @listens_for(Session, 'after_flush')
            def _after_session_flush_handler(
                session: Session, flush_context: UOWTransaction
            ) -> None:
                for obj in session.dirty | session.new | session.deleted:
                    if isinstance(obj, targets):
                        setattr(session, _custom_dirty_attr, True)
                        return

            @listens_for(Session, 'before_commit')
            def _before_session_commit_handler(session: Session) -> None:
                session_was_dirty = getattr(session, _custom_dirty_attr, False)
                if session_was_dirty:
                    cls.refresh(concurrently=True)
                    setattr(session, _custom_dirty_attr, False)
                    return

            cls._view_dependencies_handler = staticmethod(_after_session_flush_handler)
        else:
            cls._view_dependencies_handler = None

    @classmethod
    @property
    def autorefresh(cls) -> bool:
        if handler := cls._view_dependencies_handler:
            return contains(Session, 'after_flush', handler)
        return False

    @classmethod
    def refresh(cls, concurrently: bool = True) -> None:
        refresh_materialized_view(Session(), cls.__table__.fullname, concurrently)
