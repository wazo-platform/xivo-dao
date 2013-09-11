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
from xivo_dao.data_handler.exception import InvalidParametersError


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
        'version',
        'description',
    ]

    CONFIG_PARENTS = ['base', 'defaultconfigdevice']

    # mapping = {db_field: model_field}
    _MAPPING = {
        'id': 'id',
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

    @classmethod
    def from_provd(cls, device, config=None):
        filtered_device = dict((key, value) for key, value in device.iteritems() if key in cls.PROVD_KEYS)
        obj = cls(**filtered_device)

        if config:
            parents = set(config['parent_ids']) - set(cls.CONFIG_PARENTS)
            if len(parents) == 0:
                obj.template_id = 'defaultconfigdevice'
            else:
                obj.template_id = parents.pop()

        return obj

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

        parent_ids = list(self.CONFIG_PARENTS)
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
    DIRECTIONS = ['desc', 'asc']

    id = 'id'
    ip = 'ip'
    mac = 'mac'
    plugin = 'plugin'
    model = 'model'
    vendor = 'vendor'
    version = 'version'

    @classmethod
    def all_columns(cls):
        return [cls.id, cls.ip, cls.mac, cls.plugin, cls.model, cls.vendor, cls.version]

    @classmethod
    def from_column_name(cls, column):
        if column in cls.all_columns():
            return column
        return None

    @classmethod
    def directions(cls):
        return cls.DIRECTIONS

    @classmethod
    def validate_order(cls, order):
        if order not in cls.all_columns():
            raise InvalidParametersError("ordering parameter '%s' does not exist" % order)

    @classmethod
    def validate_direction(cls, direction):
        if direction not in cls.directions():
            raise InvalidParametersError("direction parameter '%s' does not exist" % direction)
