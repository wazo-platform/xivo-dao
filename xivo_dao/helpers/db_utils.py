# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager

from xivo_dao.helpers import db_manager
from xivo_dao.helpers.db_manager import daosession


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
