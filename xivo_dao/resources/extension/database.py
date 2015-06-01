# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.converters.database_converter import DatabaseConverter
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.resources.extension.model import Extension, ForwardExtension, \
    ServiceExtension, AgentActionExtension


class ServiceExtensionConverter(object):

    SERVICES = ("enablevm",
                "vmusermsg",
                "vmuserpurge",
                "phonestatus",
                "recsnd",
                "calllistening",
                "directoryaccess",
                "fwdundoall",
                "pickup",
                "callrecord",
                "incallfilter",
                "enablednd")

    @classmethod
    def typevals(cls):
        return cls.SERVICES

    def to_model(self, row):
        return ServiceExtension(id=row.id,
                                exten=row.exten,
                                service=row.typeval)


class ForwardExtensionConverter(object):

    FORWARDS = {'fwdbusy': 'busy',
                'fwdrna': 'noanswer',
                'fwdunc': 'unconditional'}

    def typevals(self):
        return self.FORWARDS.keys()

    def to_model(self, row):
        forward = self.FORWARDS[row.typeval]
        exten = self.clean_exten(row.exten)
        return ForwardExtension(id=row.id,
                                exten=exten,
                                forward=forward)

    def clean_exten(self, exten):
        return exten.strip('._')


class AgentActionExtensionConverter(object):

    ACTIONS = {'agentstaticlogin': 'login',
               'agentstaticlogoff': 'logout',
               'agentstaticlogtoggle': 'toggle'}

    def typevals(self):
        return self.ACTIONS.keys()

    def to_model(self, row):
        action = self.ACTIONS[row.typeval]
        exten = self.clean_exten(row.exten)
        return AgentActionExtension(id=row.id,
                                    exten=exten,
                                    action=action)

    def clean_exten(self, exten):
        return exten.strip('._')


class ExtensionDatabaseConverter(DatabaseConverter):

    DB_TO_MODEL_MAPPING = {
        'id': 'id',
        'exten': 'exten',
        'context': 'context',
    }

    def __init__(self):
        DatabaseConverter.__init__(self, self.DB_TO_MODEL_MAPPING, ExtensionSchema, Extension)

    def to_model(self, source):
        model = DatabaseConverter.to_model(self, source)
        self._convert_model_fields(source, model)
        return model

    def _convert_model_fields(self, source, model):
        model.commented = bool(source.commented)

    def to_source(self, model):
        source = DatabaseConverter.to_source(self, model)
        self._convert_source_fields(source, model)
        return source

    def update_source(self, source, model):
        DatabaseConverter.update_source(self, source, model)
        self._convert_source_fields(source, model)

    def _convert_source_fields(self, source, model):
        source.commented = int(model.commented)


db_converter = ExtensionDatabaseConverter()
service_converter = ServiceExtensionConverter()
fwd_converter = ForwardExtensionConverter()
agent_action_converter = AgentActionExtensionConverter()
