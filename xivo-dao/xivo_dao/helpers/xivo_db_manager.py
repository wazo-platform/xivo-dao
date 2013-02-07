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

from functools import wraps
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import OperationalError, InvalidRequestError
from sqlalchemy.orm.session import sessionmaker
import logging


logger = logging.getLogger(__name__)
dbsession = None
_XIVO_DB_URI = 'postgresql://xivo:proformatique@localhost/xivo'


def xivo_connect():
    logger.debug('Connecting to database: %s' % _XIVO_DB_URI)
    engine = create_engine(_XIVO_DB_URI)
    Session = sessionmaker(bind = engine)
    return Session()


def xivo_reconnect():
    global dbsession
    dbsession = xivo_connect()


def xivo_session():
    global dbsession
    if not dbsession:
        dbsession = xivo_connect()
    return dbsession


def _execute_with_xivo_session(func, *args, **kwargs):
    sess = xivo_session()
    result = func(sess, *args, **kwargs)
    sess.commit()
    return result


def xivo_daosession(func):

    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return _execute_with_xivo_session(func, *args, **kwargs)
        except (OperationalError, InvalidRequestError):
            logger.info("Trying to reconnect")
            xivo_reconnect()
            return _execute_with_xivo_session(func, *args, **kwargs)

    return wrapped
