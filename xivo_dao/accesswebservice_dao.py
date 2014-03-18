# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from sqlalchemy.sql.expression import and_, distinct
from xivo_dao.alchemy.accesswebservice import AccessWebService
from xivo_dao.helpers.db_manager import xivo_daosession


@xivo_daosession
def get_password(session, login):
    result = (session
              .query(AccessWebService.passwd)
              .filter(and_(AccessWebService.login == login,
                           AccessWebService.disable == 0)).first())
    if result is None:
        return None
    else:
        return result.passwd


@xivo_daosession
def get_allowed_hosts(session):
    result = (session
              .query(distinct(AccessWebService.host))
              .filter(and_(AccessWebService.host != None,
                           AccessWebService.disable == 0)).all())
    result = [item[0].encode('utf-8', 'ignore') for item in result]
    return result
