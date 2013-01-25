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
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.engine import create_engine
from xivo_dao.helpers import config

logger = logging.getLogger(__name__)

_DB_URI = config.DB_URI


class DBSessionManager(object):
    sess = None

    def connect(self):
        logger.debug('Connecting to database: %s' % _DB_URI)
        engine = create_engine(_DB_URI, echo=config.SQL_DEBUG)
        Session = sessionmaker(bind=engine)
        return Session()

    @classmethod
    def session(cls):
        if cls.sess is None:
            cls.sess = cls().connect()
        return cls.sess


def DbSession():
    return DBSessionManager.session()
