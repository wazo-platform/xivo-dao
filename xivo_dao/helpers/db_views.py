# -*- coding: utf-8 -*-
# Copyright 2020-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six

from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.ext import compiler
from sqlalchemy.schema import DDLElement, PrimaryKeyConstraint
from sqlalchemy.sql.schema import Column, MetaData, Table
from sqlalchemy.event import listen, listens_for

from .db_manager import Base, Session, daosession


__all__ = ['DDLCreateView', 'DDLDropView', 'MaterializedView', 'create_view']


class DDLCreateView(DDLElement):
    def __init__(self, name, selectable, materialized):
        self.name = name
        self.selectable = selectable
        self.materialized = materialized


class DDLDropView(DDLElement):
    def __init__(self, name, materialized, cascade=True):
        self.name = name
        self.materialized = materialized
        self.cascade = cascade


@compiler.compiles(DDLCreateView)
def _compile_create_view(element, compiler, **kw):
    materialized = ''
    if element.materialized:
        materialized = 'MATERIALIZED '

    name = compiler.dialect.identifier_preparer.quote(element.name)
    selectable = compiler.sql_compiler.process(element.selectable, literal_binds=True)

    return 'CREATE {}VIEW {} AS {}'.format(materialized, name, selectable)


@compiler.compiles(DDLDropView)
def _compile_drop_view(element, compiler, **kw):
    name = compiler.dialect.identifier_preparer.quote(element.name)

    materialized = ''
    if element.materialized:
        materialized = 'MATERIALIZED '

    cascade = ''
    if element.cascade:
        cascade = 'CASCADE'

    return 'DROP {}VIEW IF EXISTS {} {}'.format(materialized, name, cascade)


def _create_table_from_selectable(name, selectable, metadata=None, indexes=None):
    if indexes is None:
        indexes = []

    if metadata is None:
        metadata = MetaData()

    cols = indexes
    for col in selectable.c:
        cols.append(Column(col.name, col.type, primary_key=col.primary_key))

    table = Table(name, metadata, *cols)
    if not any([col.primary_key for col in selectable.columns]):
        table.append_constraint(
            PrimaryKeyConstraint(*[col.name for col in selectable.columns])
        )

    return table


def create_view(name, selectable, materialized=True, indexes=None):
    metadata = Base.metadata
    table = _create_table_from_selectable(name, selectable, indexes=indexes)

    listen(metadata, 'after_create', DDLCreateView(name, selectable, materialized))
    listen(metadata, 'before_drop', DDLDropView(name, materialized))

    if materialized:
        @listens_for(metadata, 'after_create')
        def create_indexes(target, connection, **kw):
            for idx in table.indexes:
                idx.create(connection)

    return table


class _MaterializedViewMeta(DeclarativeMeta):
    def __init__(self, name, bases, dict):
        super(_MaterializedViewMeta, self).__init__(name, bases, dict)
        self._track_dependencies()

    @daosession
    def refresh(session, self, concurrently=True):
        view_name = session.bind.engine.dialect.identifier_preparer.quote(
            self.__table__.fullname
        )

        concurrent = ''
        if concurrently:
            concurrent = 'CONCURRENTLY '

        session.execute('REFRESH MATERIALIZED VIEW {}{}'.format(concurrent, view_name))

    def _track_dependencies(self):
        targets = getattr(self, '__view_dependencies__', None)
        if targets:
            @listens_for(Session, 'before_commit')
            def _before_session_commit_handler(session):
                for obj in session:
                    if isinstance(obj, tuple(targets)):
                        self.refresh(concurrently=True)
                        return


@six.add_metaclass(_MaterializedViewMeta)
class MaterializedView(Base):
    __abstract__ = True
