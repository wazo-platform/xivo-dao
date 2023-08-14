# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from typing import NamedTuple

from xivo.xivo_helpers import clean_extension


class ServiceExtension(NamedTuple):
    id: int
    exten: str
    service: str


class ForwardExtension(NamedTuple):
    id: int
    exten: str
    forward: str


class AgentActionExtension(NamedTuple):
    id: int
    exten: str
    action: str


class ServiceExtensionConverter:

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
        exten = clean_extension(row.exten)
        return ServiceExtension(id=row.id,
                                exten=exten,
                                service=row.typeval)


class ForwardExtensionConverter:

    FORWARDS = {'fwdbusy': 'busy',
                'fwdrna': 'noanswer',
                'fwdunc': 'unconditional'}

    TYPEVALS = {value: key for key, value in FORWARDS.items()}

    def typevals(self):
        return list(self.FORWARDS.keys())

    def to_typeval(self, forward):
        return self.TYPEVALS[forward]

    def to_forward(self, typeval):
        return self.FORWARDS[typeval]

    def to_model(self, row):
        forward = self.FORWARDS[row.typeval]
        exten = clean_extension(row.exten)
        return ForwardExtension(id=row.id,
                                exten=exten,
                                forward=forward)


class AgentActionExtensionConverter:

    ACTIONS = {'agentstaticlogin': 'login',
               'agentstaticlogoff': 'logout',
               'agentstaticlogtoggle': 'toggle'}

    TYPEVALS = {value: key for key, value in ACTIONS.items()}

    def typevals(self):
        return list(self.ACTIONS.keys())

    def to_typeval(self, action):
        return self.TYPEVALS[action]

    def to_action(self, typeval):
        return self.ACTIONS[typeval]

    def to_model(self, row):
        action = self.ACTIONS[row.typeval]
        exten = clean_extension(row.exten)
        return AgentActionExtension(id=row.id,
                                    exten=exten,
                                    action=action)


class GroupMemberActionExtensionConverter:

    ACTIONS = {'groupmemberjoin': 'join',
               'groupmemberleave': 'leave',
               'groupmembertoggle': 'toggle'}

    TYPEVALS = {value: key for key, value in ACTIONS.items()}

    def typevals(self):
        return list(self.ACTIONS.keys())

    def to_typeval(self, action):
        return self.TYPEVALS[action]

    def to_action(self, typeval):
        return self.ACTIONS[typeval]

    def to_model(self, row):
        action = self.ACTIONS[row.typeval]
        exten = clean_extension(row.exten)
        return AgentActionExtension(id=row.id,
                                    exten=exten,
                                    action=action)


agent_action_converter = AgentActionExtensionConverter()
fwd_converter = ForwardExtensionConverter()
group_member_action_converter = GroupMemberActionExtensionConverter()
service_converter = ServiceExtensionConverter()
