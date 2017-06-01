# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

import six

from xivo_dao.resources.extension.model import ForwardExtension, \
    ServiceExtension, AgentActionExtension


def clean_exten(exten):
    return exten.strip('_.')


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
        exten = clean_exten(row.exten)
        return ServiceExtension(id=row.id,
                                exten=exten,
                                service=row.typeval)


class ForwardExtensionConverter(object):

    FORWARDS = {'fwdbusy': 'busy',
                'fwdrna': 'noanswer',
                'fwdunc': 'unconditional'}

    TYPEVALS = {value: key for key, value in six.iteritems(FORWARDS)}

    def typevals(self):
        return self.FORWARDS.keys()

    def to_typeval(self, forward):
        return self.TYPEVALS[forward]

    def to_forward(self, typeval):
        return self.FORWARDS[typeval]

    def to_model(self, row):
        forward = self.FORWARDS[row.typeval]
        exten = clean_exten(row.exten)
        return ForwardExtension(id=row.id,
                                exten=exten,
                                forward=forward)


class AgentActionExtensionConverter(object):

    ACTIONS = {'agentstaticlogin': 'login',
               'agentstaticlogoff': 'logout',
               'agentstaticlogtoggle': 'toggle'}

    TYPEVALS = {value: key for key, value in six.iteritems(ACTIONS)}

    def typevals(self):
        return self.ACTIONS.keys()

    def to_typeval(self, action):
        return self.TYPEVALS[action]

    def to_action(self, typeval):
        return self.ACTIONS[typeval]

    def to_model(self, row):
        action = self.ACTIONS[row.typeval]
        exten = clean_exten(row.exten)
        return AgentActionExtension(id=row.id,
                                    exten=exten,
                                    action=action)


service_converter = ServiceExtensionConverter()
fwd_converter = ForwardExtensionConverter()
agent_action_converter = AgentActionExtensionConverter()
