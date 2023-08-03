# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar

# Note: Proper interface for loader strategy are implemented in SQLAlchemy >= 1.4
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.strategy_options import Load, loader_option


class QueryOptionsMixin:
    __ctx_query_options: ContextVar[tuple[Load | loader_option] | None] = ContextVar(
        'query_options', default=None
    )

    def _generate_query(self) -> Query:
        query = self.session.query(self._search_table)
        options = self.__ctx_query_options.get()
        if options:
            query = query.options(*options)
        return query

    @classmethod
    @contextmanager
    def context_query_options(cls, *options: Load | loader_option):
        memento = cls.__ctx_query_options.set(options)
        try:
            yield
        finally:
            cls.__ctx_query_options.reset(memento)
