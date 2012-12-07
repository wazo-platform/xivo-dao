# -*- coding: UTF-8 -*-

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, xivo-dao is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which xivo-dao
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy import dbconnection
from sqlalchemy import and_

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


class PhoneFunckeyDAO(object):

    def __init__(self):
        pass

    def _get_dest(self, user_id, fwd_type):
        destinations = (_session().query(PhoneFunckey.exten)
                        .filter(and_(PhoneFunckey.iduserfeatures == user_id,
                                     PhoneFunckey.typevalextenumbers == fwd_type)))

        destinations = [d.exten if d.exten else '' for d in destinations.all()]

        return destinations

    def get_dest_unc(self, user_id):
        return self._get_dest(user_id, 'fwdunc')

    def get_dest_rna(self, user_id):
        return self._get_dest(user_id, 'fwdrna')

    def get_dest_busy(self, user_id):
        return self._get_dest(user_id, 'fwdbusy')
