# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager
from xivo_dao.helpers import db_manager
from xivo_dao.helpers.db_manager import daosession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement, Executable, _literal_as_text


class Explain(Executable, ClauseElement):
    '''
    Helper to run an SQL Explain [Analyze] on a query

    typical usage in-code:

    `result = self.session.execute(Explain(some_query, analyze=True)).fetchall()`
    '''

    def __init__(self, stmt, analyze=False):
        self.statement = _literal_as_text(stmt)
        self.analyze = analyze


@compiles(Explain, "postgresql")
def _pg_explain(element, compiler, **kw):
    text = "EXPLAIN "
    if element.analyze:
        text += "ANALYZE "
    text += compiler.process(element.statement, **kw)

    return text


@contextmanager
def flush_session(session):
    try:
        yield
        session.flush()
    except Exception:
        session.rollback()
        raise


@daosession
def get_dao_session(session):
    return session


@contextmanager
def session_scope(read_only=False):
    session = db_manager.Session()
    try:
        yield session
        if not read_only:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        db_manager.Session.remove()
