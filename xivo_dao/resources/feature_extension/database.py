# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import NamedTuple

from xivo.xivo_helpers import clean_extension


class ServiceFeatureExtension(NamedTuple):
    uuid: str
    exten: str
    service: str


class ForwardFeatureExtension(NamedTuple):
    uuid: str
    exten: str
    forward: str


class AgentActionFeatureExtension(NamedTuple):
    uuid: str
    exten: str
    action: str


class ServiceFeatureExtensionConverter:
    SERVICES = (
        "enablevm",
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
        "enablednd",
    )

    @classmethod
    def features(cls):
        return cls.SERVICES

    def to_model(self, row):
        exten = clean_extension(row.exten)
        return ServiceFeatureExtension(uuid=row.uuid, exten=exten, service=row.feature)


class ForwardFeatureExtensionConverter:
    FORWARDS = {'fwdbusy': 'busy', 'fwdrna': 'noanswer', 'fwdunc': 'unconditional'}

    FEATURES = {value: key for key, value in FORWARDS.items()}

    def features(self):
        return list(self.FORWARDS.keys())

    def to_feature(self, forward):
        return self.FEATURES[forward]

    def to_forward(self, feature):
        return self.FORWARDS[feature]

    def to_model(self, row):
        forward = self.FORWARDS[row.feature]
        exten = clean_extension(row.exten)
        return ForwardFeatureExtension(uuid=row.uuid, exten=exten, forward=forward)


class AgentActionFeatureExtensionConverter:
    ACTIONS = {
        'agentstaticlogin': 'login',
        'agentstaticlogoff': 'logout',
        'agentstaticlogtoggle': 'toggle',
    }

    FEATURES = {value: key for key, value in ACTIONS.items()}

    def features(self):
        return list(self.ACTIONS.keys())

    def to_feature(self, action):
        return self.FEATURES[action]

    def to_action(self, feature):
        return self.ACTIONS[feature]

    def to_model(self, row):
        action = self.ACTIONS[row.feature]
        exten = clean_extension(row.exten)
        return AgentActionFeatureExtension(uuid=row.uuid, exten=exten, action=action)


class GroupMemberActionFeatureExtensionConverter:
    ACTIONS = {
        'groupmemberjoin': 'join',
        'groupmemberleave': 'leave',
        'groupmembertoggle': 'toggle',
    }

    FEATURES = {value: key for key, value in ACTIONS.items()}

    def features(self):
        return list(self.ACTIONS.keys())

    def to_feature(self, action):
        return self.FEATURES[action]

    def to_action(self, feature):
        return self.ACTIONS[feature]

    def to_model(self, row):
        action = self.ACTIONS[row.feature]
        exten = clean_extension(row.exten)
        return AgentActionFeatureExtension(uuid=row.uuid, exten=exten, action=action)


agent_action_converter = AgentActionFeatureExtensionConverter()
fwd_converter = ForwardFeatureExtensionConverter()
group_member_action_converter = GroupMemberActionFeatureExtensionConverter()
service_converter = ServiceFeatureExtensionConverter()
