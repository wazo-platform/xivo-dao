# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.types import Enum

from xivo_dao.helpers.db_manager import Base

dialaction_action = Enum(
    'none',
    'endcall:busy',
    'endcall:congestion',
    'endcall:hangup',
    'user',
    'group',
    'queue',
    'voicemail',
    'extension',
    'outcall',
    'application:callbackdisa',
    'application:disa',
    'application:directory',
    'application:faxtomail',
    'application:voicemailmain',
    'application:password',
    'sound',
    'custom',
    'ivr',
    'conference',
    'switchboard',
    'application:custom',
    name='dialaction_action',
    metadata=Base.metadata,
)

dialaction_category = Enum(
    'callfilter',
    'group',
    'incall',
    'queue',
    'user',
    'ivr',
    'ivr_choice',
    'switchboard',
    name='dialaction_category',
    metadata=Base.metadata,
)

extenumbers_type = Enum(
    'extenfeatures',
    'featuremap',
    'generalfeatures',
    'group',
    'incall',
    'outcall',
    'queue',
    'user',
    'voicemenu',
    'conference',
    'parking',
    name='extenumbers_type',
    metadata=Base.metadata,
)

callfilter_type = Enum('bosssecretary', name='callfilter_type', metadata=Base.metadata)

callfilter_bosssecretary = Enum(
    'bossfirst-serial',
    'bossfirst-simult',
    'secretary-serial',
    'secretary-simult',
    'all',
    name='callfilter_bosssecretary',
    metadata=Base.metadata,
)

callfilter_callfrom = Enum(
    'internal', 'external', 'all', name='callfilter_callfrom', metadata=Base.metadata
)

generic_bsfilter = Enum(
    'no', 'boss', 'secretary', name='generic_bsfilter', metadata=Base.metadata
)

netiface_type = Enum('iface', name='netiface_type', metadata=Base.metadata)

schedule_path_type = Enum(
    'user',
    'group',
    'queue',
    'incall',
    'outcall',
    'voicemenu',
    name='schedule_path_type',
    metadata=Base.metadata,
)

stat_switchboard_endtype = Enum(
    'abandoned',
    'completed',
    'forwarded',
    'transferred',
    name='stat_switchboard_endtype',
    metadata=Base.metadata,
)

valid_trunk_protocols = [
    'sip',
    'iax',
    'sccp',
    'custom',
]
trunk_protocol = Enum(
    *valid_trunk_protocols, name='trunk_protocol', metadata=Base.metadata
)

voicemail_accesstype = Enum(
    'personal', 'global', name='voicemail_accesstype', metadata=Base.metadata
)
