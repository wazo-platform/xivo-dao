# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six

from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.event import listens_for
from sqlalchemy.exc import InvalidRequestError, NoInspectionAvailable
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.selectable import Selectable

try:
    # sqlalchemy_utils is python3 only
    from sqlalchemy_utils import (
        refresh_materialized_view,
        create_materialized_view as _create_materialized_view,
    )
except ImportError:
    pass

from .db_manager import Base, Session, daosession


def create_materialized_view(name, selectable, dependencies=None, indexes=None):
    """
    Create a materialized view

    :param name: The name of the view to create.
    :param selectable: An SQLAlchemy selectable e.g. a select() statement.
    :param dependencies:
        An optional list of models to depend on.  Modifying, adding or removing
        an instance of these models in the database will trigger the view to update itself.
    :param indexes: An optional list of SQLAlchemy Index instances.

    """
    dependencies = dependencies or []
    indexes = indexes or []

    if not name:
        raise ValueError('View must have a name')

    if not isinstance(selectable, Selectable):
        raise ValueError("Invalid View selectable, must be an SQLAlchemy Selectable.")

    for dependency in dependencies:
        try:
            inspect(dependency.__mapper__)
        except (NoInspectionAvailable, AttributeError):
            raise ValueError(
                'Invalid view dependency, must be an SQLAlchemy mapped class'
            )

    table = _create_materialized_view(name, selectable, Base.metadata, indexes)
    return {'table': table, 'dependencies': dependencies}


class _MaterializedViewMeta(DeclarativeMeta):
    def __init__(self, clsname, bases, attrs):
        for cls_ in bases:
            if cls_.__name__ == 'MaterializedView' and not hasattr(self, '__view__'):
                raise InvalidRequestError(
                    "Class '{}' must specify a '__view__' attribute".format(self)
                )
        try:
            view = getattr(self, '__view__')
            self.__table__ = view['table']
            self._view_dependencies = view['dependencies']
        except AttributeError:
            pass
        except (TypeError, KeyError):
            raise InvalidRequestError(
                "__view__ is invalid, use 'create_materialized_view' helper function"
            )
        super(_MaterializedViewMeta, self).__init__(clsname, bases, attrs)
        self._track_dependencies()

    @daosession
    def refresh(session, self, concurrently=True):
        refresh_materialized_view(session, self.__table__.fullname, concurrently)

    def _track_dependencies(self):
        if not hasattr(self, '_view_dependencies'):
            return
        targets = self._view_dependencies
        if targets:

            @listens_for(Session, 'before_commit')
            def _before_session_commit_handler(session):
                for obj in session:
                    if isinstance(obj, tuple(targets)):
                        self.refresh(concurrently=True)
                        return


@six.add_metaclass(_MaterializedViewMeta)
class MaterializedView(Base):
    """
    Materialized View base class

    Used to tell SQLAlchemy to construct a materialized view.

    Usage:

    Assign the '__view__' attribute using the create_materialized_view function
    """

    __abstract__ = True
