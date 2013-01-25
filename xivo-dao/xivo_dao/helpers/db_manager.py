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
from xivo import config
from xivo_dao.alchemy import dbconnection

logger = logging.getLogger(__name__)


class DBManager(object):

    def connect(self):
        logger.debug('Connecting to database')
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)
        dbconnection.add_connection_as(config.DB_URI, 'asterisk')

    def disconnect(self):
        logger.debug('Disconnecting to database')
        dbconnection.unregister_db_connection_pool()

    def reconnect(self):
        logger.info('Reconnecting to database')
        self.disconnect()
        self.connect()
