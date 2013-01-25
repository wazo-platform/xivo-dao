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

logger = logging.getLogger(__name__)

_DB_URI = config.DB_URI

dbsession = None

def connect():
    logger.debug('Connecting to database: %s' % _DB_URI)
    engine = create_engine(_DB_URI, echo=config.SQL_DEBUG)
    Session = sessionmaker(bind=engine)
    return Session()


def session():
    global dbsession
    if not dbsession:
        dbsession = connect()
    return dbsession


def daosession(session, func):

    @wraps(func)
    def wrapped(session, *args, **kwargs):
        sess = session()
        try:
            sess.begin()
            result = func(sess, *args, **kwargs)
            sess.commit()
            return result
        except (OperationalError, InvalidRequestError):
            logger.debug('Trying to reconnect')
            new_sess = session()
            result = func(new_sess, *args, **kwargs)
            new_sess.commit()
            return result

    return wrapped
