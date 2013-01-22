# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.devicefeatures import DeviceFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_peer_name(device_id):
    row = (_session()
           .query(LineFeatures.name, LineFeatures.protocol)
           .filter(LineFeatures.device == str(device_id))).first()

    if not row:
        raise LookupError('No such device')

    return '/'.join([row.protocol, row.name])


def get_vendor_model(device_id):
    row = (_session()
           .query(DeviceFeatures.vendor, DeviceFeatures.model)
           .filter(DeviceFeatures.id == device_id)).first()

    if not row:
        raise LookupError('No such device')

    return row.vendor, row.model
