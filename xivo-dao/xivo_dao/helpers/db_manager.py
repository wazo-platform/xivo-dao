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
from xivo_dao.helpers.notifiers.amqp.publisher import AMQPPublisher

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

_asterisk_engine = None
AsteriskSession = None

_xivo_engine = None
XivoSession = None

BusPublisher = None


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
    _init_asterisk()
    _init_xivo()
    _init_bus()


def _init_bus():
    global BusPublisher
    bus_publisher = AMQPPublisher()
    bus_publisher.connect('localhost', 5672)
    BusPublisher = bus_publisher


def _init_asterisk():
    global _asterisk_engine
    global AsteriskSession
    _asterisk_engine = _new_engine(config.DB_URI)
    AsteriskSession = _new_scoped_session(_asterisk_engine)


def _init_xivo():
    global _xivo_engine
    global XivoSession
    _xivo_engine = _new_engine(config.XIVO_DB_URI)
    XivoSession = _new_scoped_session(_xivo_engine)


def _new_engine(url):
    return create_engine(url, echo=config.SQL_DEBUG)


def _new_scoped_session(engine):
    return scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=True))


def reinit():
    AsteriskSession.close()
    _asterisk_engine.dispose()

    XivoSession.close()
    _xivo_engine.dispose()

    _init()


_init()
