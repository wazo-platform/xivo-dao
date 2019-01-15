# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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
        return list(self.FORWARDS.keys())

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
        return list(self.ACTIONS.keys())

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
