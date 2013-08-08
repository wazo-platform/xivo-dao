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

from xivo_dao.helpers.abstract_model import AbstractModels
from xivo_dao.alchemy.devicefeatures import DeviceFeatures as DeviceSchema


class Device(AbstractModels):

    MANDATORY = [
    ]

    # mapping = {db_field: model_field}
    _MAPPING = {
        'id': 'id',
        'deviceid': 'deviceid',
        'config': 'config',
        'plugin': 'plugin',
        'ip': 'ip',
        'mac': 'mac',
        'sn': 'sn',
        'vendor': 'vendor',
        'model': 'model',
        'version': 'version',
        'proto': 'proto',
        'internal': 'internal',
        'configured': 'configured',
        'commented': 'commented',
        'description': 'description',
    }

    _RELATION = {}

    def __init__(self, *args, **kwargs):
        AbstractModels.__init__(self, *args, **kwargs)


class DeviceOrdering(object):
    ip = DeviceSchema.ip
    mac = DeviceSchema.mac
