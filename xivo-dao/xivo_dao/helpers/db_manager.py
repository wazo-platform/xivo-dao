# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
from functools import wraps
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.engine import create_engine
from xivo_dao.helpers import config
from sqlalchemy.exc import OperationalError, InterfaceError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session

logger = logging.getLogger(__name__)


def todict(self):
    d = {}
    for c in self.__table__.columns:
        value = getattr(self, c.name.replace('-', '_'))
        d[c.name] = value

    return d


Base = declarative_base()
Base.todict = todict

Type = declarative_base()

AsteriskSession = None
XivoSession = None


def daosession(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return _execute_with_session(AsteriskSession, func, args, kwargs)
    return wrapped


def xivo_daosession(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return _execute_with_session(XivoSession, func, args, kwargs)
    return wrapped


def _execute_with_session(session_class, func, args, kwargs):
    try:
        session = session_class()
        return _apply_and_flush(func, session, args, kwargs)
    except (OperationalError, InterfaceError) as e:
        logger.warning('error while executing request in DB: %s', e)
        session_class.remove()
        session = session_class()
        return _apply_and_flush(func, session, args, kwargs)


def _apply_and_flush(func, session, args, kwargs):
    result = func(session, *args, **kwargs)
    session.flush()
    return result


def _init():
    global AsteriskSession
    AsteriskSession = _new_scoped_session(config.DB_URI)
    global XivoSession
    XivoSession = _new_scoped_session(config.XIVO_DB_URI)


def _new_scoped_session(url):
    engine = create_engine(url, echo=config.SQL_DEBUG)
    return scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=True))


_init()
