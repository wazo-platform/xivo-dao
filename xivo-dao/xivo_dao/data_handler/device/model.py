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

    PROVD_KEYS = [
        'id',
        'ip',
        'mac',
        'plugin',
        'vendor',
        'model',
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
        'template_id': 'template_id',
    }

    _RELATION = {}

    def __init__(self, *args, **kwargs):
        AbstractModels.__init__(self, *args, **kwargs)

    def to_provd_device(self):
        parameters = self._filter_device_parameters()

        if 'mac' in parameters:
            parameters['mac'] = parameters['mac'].lower()

        return parameters

    def _filter_device_parameters(self):
        parameters = {}
        for key in self.PROVD_KEYS:
            if hasattr(self, key):
                parameters[key] = getattr(self, key)

        return parameters

    def to_provd_config(self):
        template_id = getattr(self, 'template_id', 'defaultconfigdevice')

        parent_ids = ['base', 'defaultconfigdevice']
        if template_id not in parent_ids:
            parent_ids.append(template_id)

        return {
            'id': self.id,
            'configdevice': template_id,
            'deletable': True,
            'parent_ids': parent_ids,
            'raw_config': {}
        }


class DeviceOrdering(object):
    ip = DeviceSchema.ip
    mac = DeviceSchema.mac
