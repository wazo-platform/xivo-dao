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
from sqlalchemy.exc import InvalidRequestError, OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session

logger = logging.getLogger(__name__)

dbsession = None
xivo_dbsession = None
ASTERISK_DB_NAME = 'asterisk'
XIVO_DB_NAME = 'xivo'


def todict(self):
    d = {}
    for c in self.__table__.columns:
        value = getattr(self, c.name.replace('-', '_'))
        d[c.name] = value

    return d


Base = declarative_base()
Base.todict = todict

Type = declarative_base()


def connect(db_name=ASTERISK_DB_NAME):
    db_uri = ''
    if db_name == ASTERISK_DB_NAME:
        db_uri = config.DB_URI
    elif db_name == XIVO_DB_NAME:
        db_uri = config.XIVO_DB_URI
    else:
        logger.error('Unknown database name provided: ' + str(db_name))
        return None
    logger.debug('Connecting to database: %s' % db_uri)
    engine = create_engine(db_uri, echo=config.SQL_DEBUG)
    Session = scoped_session(sessionmaker())
    Session.configure(bind=engine, autoflush=False, autocommit=True)
    return Session()


def reconnect(db_name=ASTERISK_DB_NAME):
    if db_name == ASTERISK_DB_NAME:
        global dbsession
        dbsession = connect(db_name)
    elif db_name == XIVO_DB_NAME:
        global xivo_dbsession
        xivo_dbsession = connect(db_name)


def session(db_name=ASTERISK_DB_NAME):
    if db_name == ASTERISK_DB_NAME:
        global dbsession
        if not dbsession:
            dbsession = connect(db_name)
        return dbsession
    if db_name == XIVO_DB_NAME:
        global xivo_dbsession
        if not xivo_dbsession:
            xivo_dbsession = connect(db_name)
        return xivo_dbsession


def _execute_with_session(func, db_name, *args, **kwargs):
    sess = session(db_name)
    result = func(sess, *args, **kwargs)
    sess.flush()
    return result


def daosession(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return _execute_with_session(func, ASTERISK_DB_NAME, *args, **kwargs)
        except (OperationalError, InvalidRequestError):
            logger.info("Trying to reconnect to asterisk")
            reconnect(ASTERISK_DB_NAME)
            return _execute_with_session(func, ASTERISK_DB_NAME, *args, **kwargs)

    return wrapped


def xivo_daosession(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return _execute_with_session(func, XIVO_DB_NAME, *args, **kwargs)
        except (OperationalError, InvalidRequestError):
            logger.info("Trying to reconnect to xivo")
            reconnect(XIVO_DB_NAME)
            return _execute_with_session(func, XIVO_DB_NAME, *args, **kwargs)

    return wrapped
