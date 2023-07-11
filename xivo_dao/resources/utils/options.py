# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager
from contextvars import ContextVar


class QueryOptionsMixin:
    __ctx_query_options = ContextVar('query_options', default=None)

    def _generate_query(self):
        query = self.session.query(self._search_table)
        options = self.__ctx_query_options.get()
        if options:
            query = query.options(*options)
        return query

    @classmethod
    @contextmanager
    def query_options(cls, *options):
        memento = cls.__ctx_query_options.set(options)
        try:
            yield
        finally:
            cls.__ctx_query_options.reset(memento)
