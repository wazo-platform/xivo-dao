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


from xivo_dao.alchemy.devicefeatures import DeviceFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.helpers.db_manager import daosession

@daosession
def get_peer_name(session, device_id):
    row = (session
           .query(LineFeatures.name, LineFeatures.protocol)
           .filter(LineFeatures.device == str(device_id))).first()

    if not row:
        raise LookupError('No such device')

    return '/'.join([row.protocol, row.name])


@daosession
def get_vendor_model(session, device_id):
    row = (session
           .query(DeviceFeatures.vendor, DeviceFeatures.model)
           .filter(DeviceFeatures.id == device_id)).first()

    if not row:
        raise LookupError('No such device')

    return row.vendor, row.model


@daosession
def get_deviceid(session, db_id):
    return session.query(DeviceFeatures.deviceid).filter(DeviceFeatures.id == db_id).first()[0]


