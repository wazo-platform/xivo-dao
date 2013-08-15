# -*- coding: utf-8 -*-
#
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
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema


class Line(AbstractModels):

    MANDATORY = [
        'context',
        'protocol'
    ]

    # mapping = {db_field: model_field}
    _MAPPING = {
        'id': 'id',
        'name': 'name',
        'number': 'number',
        'context': 'context',
        'protocol': 'protocol',
        'protocolid': 'protocolid',
        'callerid': 'callerid',
        'device': 'device',
        'provisioningid': 'provisioning_extension',
        'configregistrar': 'configregistrar',
        'num': 'device_slot'
    }

    _RELATION = {}

    def __init__(self, *args, **kwargs):
        AbstractModels.__init__(self, *args, **kwargs)

    @property
    def interface(self):
        return '%s/%s' % (self.protocol.upper(), self.name)


class LineOrdering(object):
        name = LineSchema.name
        context = LineSchema.context


class LineSIP(Line):

    # mapping = {db_field: model_field}
    _MAPPING = dict(Line._MAPPING.items() + {
        'username': 'username',
        'secret': 'secret'
    }.items())

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        self.protocol = 'sip'

    @classmethod
    def from_data_source(cls, db_object):
        obj = super(LineSIP, cls).from_data_source(db_object)
        if hasattr(obj, 'name'):
            obj.username = db_object.name
        return obj

    def to_data_source(self, class_schema):
        obj = AbstractModels.to_data_source(self, class_schema)
        if hasattr(self, 'username'):
            obj.name = self.username
        del obj.username
        return obj

    def to_data_dict(self):
        data_dict = AbstractModels.to_data_dict(self)
        if hasattr(self, 'username'):
            data_dict['name'] = self.username
        del data_dict['username']
        return data_dict

    def update_from_data_source(self, db_object):
        AbstractModels.update_from_data_source(self, db_object)
        if hasattr(db_object, 'name'):
            self.username = db_object.name

    def update_data_source(self, db_object):
        AbstractModels.update_data_source(self, db_object)
        if hasattr(self, 'username'):
            setattr(db_object, 'name', self.username)
        setattr(db_object, 'username', '')


class LineIAX(Line):

    # mapping = {db_field: model_field}
    _MAPPING = dict(Line._MAPPING.items() + {
        'username': 'username',
        'secret': 'secret'
    }.items())

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        self.protocol = 'iax'


class LineSCCP(Line):

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        self.protocol = 'sccp'


class LineCUSTOM(Line):

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        self.protocol = 'custom'
