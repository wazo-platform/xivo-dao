# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

_dao_engine = None
_DaoSession = None


def daosession(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not _DaoSession:
            _init()
        return _execute_with_session(_DaoSession, func, args, kwargs)
    return wrapped


def _execute_with_session(session_class, func, args, kwargs):
    try:
        session = session_class()
        return _apply_and_flush(func, session, args, kwargs)
    except (OperationalError, InterfaceError) as e:
        logger.warning('error while executing request in DB: %s', e)
        logger.info('reinitializing the DB connection and retrying the request')
        reinit()
        session = session_class()
        return _apply_and_flush(func, session, args, kwargs)


def _apply_and_flush(func, session, args, kwargs):
    result = func(session, *args, **kwargs)
    session.flush()
    return result


def _init():
    _init_asterisk(config.DB_URI)


def _init_asterisk(url):
    global _dao_engine
    global _DaoSession

    _dao_engine = _new_engine(url)
    _DaoSession = _new_scoped_session(_dao_engine)


def _new_engine(url):
    return create_engine(url, echo=config.SQL_DEBUG)


def _new_scoped_session(engine):
    return scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=True))


def reinit():
    close()
    _init()


def close():
    _DaoSession.close()
    _dao_engine.dispose()
