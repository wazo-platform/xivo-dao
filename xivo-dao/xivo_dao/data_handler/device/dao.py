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

from xivo_dao.alchemy.devicefeatures import DeviceFeatures as DeviceSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.exception import ElementNotExistsError


@daosession
def get(session, device_id):
    try:
        res = (session.query(DeviceSchema).filter(DeviceSchema.id == int(device_id))).first()
    except ValueError:
        raise ElementNotExistsError('Device', id=device_id)

    if not res:
        raise ElementNotExistsError('Device', id=device_id)

    return Device.from_data_source(res)


@daosession
def get_by_deviceid(session, device_id):
    res = (session.query(DeviceSchema).filter(DeviceSchema.deviceid == device_id)).first()

    if not res:
        raise ElementNotExistsError('Device', deviceid=device_id)

    return Device.from_data_source(res)
