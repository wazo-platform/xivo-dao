# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class UserDirectory:
    def __init__(
        self,
        id,
        uuid,
        line_id,
        agent_id,
        firstname,
        lastname,
        exten,
        email,
        mobile_phone_number,
        voicemail_number,
        userfield,
        description,
        context,
    ):
        self.id = id
        self.uuid = uuid
        self.line_id = line_id
        self.agent_id = agent_id
        self.firstname = firstname
        self.lastname = lastname
        self.exten = exten
        self.email = email
        self.mobile_phone_number = mobile_phone_number
        self.voicemail_number = voicemail_number
        self.userfield = userfield
        self.description = description
        self.context = context

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class UserSummary:
    def __init__(
        self,
        id,
        uuid,
        firstname,
        lastname,
        email,
        enabled,
        provisioning_code,
        protocol,
        extension,
        context,
        subscription_type,
    ):
        self.id = id
        self.uuid = uuid
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.enabled = enabled
        self.provisioning_code = provisioning_code
        self.protocol = protocol
        self.extension = extension
        self.context = context
        self.subscription_type = subscription_type

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
