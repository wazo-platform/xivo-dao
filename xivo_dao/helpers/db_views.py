# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six

from sqlalchemy import Column, MetaData, PrimaryKeyConstraint, Table, Index
from sqlalchemy.ext import compiler
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.event import listens_for, listen, contains
from sqlalchemy.exc import InvalidRequestError, NoInspectionAvailable
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.ddl import DDLElement
from sqlalchemy.sql.selectable import Selectable

from .db_manager import Base, Session, daosession


# Adapted from:
# * https://github.com/jeffwidman/sqlalchemy-postgresql-materialized-views
# * https://github.com/kvesteri/sqlalchemy-utils
#
# Notes:
# * SQLAlchemy-utils package provides utilities for database views
#   Until wazo-platform fully drops python2 support, we cannot use recent enough sqlalchemy-utils
#   because of packaging issues, forcing the custom implementation below


# Todo: Replace by SQLAlchemy-Utils when possible
class CreateView(DDLElement):
    def __init__(self, name, selectable, materialized):
        self.name = name
        self.selectable = selectable
        self.materialized = materialized


@compiler.compiles(CreateView)
def _compile_create_view(element, compiler, **kw):
    name = compiler.dialect.identifier_preparer.quote(element.name)
    selectable = compiler.sql_compiler.process(element.selectable, literal_binds=True)
    materialized = 'MATERIALIZED ' if element.materialized else ''

    return 'CREATE {}VIEW {} AS {}'.format(materialized, name, selectable)


# Todo: Replace by SQLAlchemy-Utils when possible
class DropView(DDLElement):
    def __init__(self, name, materialized, cascade=True):
        self.name = name
        self.materialized = materialized
        self.cascade = cascade


@compiler.compiles(DropView)
def _compile_drop_view(element, compiler, **kw):
    name = compiler.dialect.identifier_preparer.quote(element.name)
    materialized = 'MATERIALIZED ' if element.materialized else ''
    cascade = 'CASCADE ' if element.cascade else ''

    return 'DROP {}VIEW IF EXISTS {} {}'.format(materialized, name, cascade)


# Replace by SQLAlchemy-Utils when possible
def _create_table_from_selectable(name, selectable, indexes=None, **kwargs):
    indexes = indexes or []
    metadata = MetaData()

    cols = indexes
    for col in selectable.columns:
        cols.append(Column(col.name, col.type, primary_key=col.primary_key))

    table = Table(name, metadata, *cols)
    if not any([col.primary_key for col in selectable.columns]):
        table.append_constraint(
            PrimaryKeyConstraint(*[col.name for col in selectable.columns])
        )

    return table


# Todo: Replace by SQLAlchemy-Utils when possible
def _create_materialized_view(name, selectable, metadata, indexes=None, **kwargs):
    table = _create_table_from_selectable(name, selectable, indexes=indexes)

    listen(metadata, 'after_create', CreateView(name, selectable, True))
    listen(metadata, 'before_drop', DropView(name, True))

    @listens_for(metadata, 'after_create')
    def create_indexes(target, connection, **kw):
        for idx in table.indexes:
            idx.create(connection)

    return table


# Todo: Replace by SQLAlchemy-Utils when possible
def _refresh_materialized_view(session, name, concurrently):
    view_name = session.bind.engine.dialect.identifier_preparer.quote(name)
    concurrently = 'CONCURRENTLY ' if concurrently else ''

    session.flush()
    session.execute('REFRESH MATERIALIZED VIEW {}{}'.format(concurrently, view_name))


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

    for index in indexes:
        if not isinstance(index, Index):
            raise ValueError('Invalid view index, must be an SQLAlchemy index')

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
        self._view_dependencies_handler = None
        self._track_dependencies()

    @daosession
    def refresh(session, self, concurrently=True):
        _refresh_materialized_view(session, self.__table__.fullname, concurrently)

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

            self._view_dependencies_handler = staticmethod(
                _before_session_commit_handler
            )

    @property
    def autorefresh(self):
        return contains(Session, 'before_commit', self._view_dependencies_handler)


@six.add_metaclass(_MaterializedViewMeta)
class MaterializedView(Base):
    """
    Materialized View base class

    Used to tell SQLAlchemy to construct a materialized view.

    Usage:

    Assign the '__view__' attribute using the create_materialized_view function
    """

    __abstract__ = True