# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

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
def session_scope():
    session = db_manager.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        db_manager.Session.remove()
