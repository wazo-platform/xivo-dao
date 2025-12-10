# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload, lazyload, selectinload

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.endpoint_sip_section import EndpointSIPSection
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.pickup import Pickup
from xivo_dao.alchemy.pickupmember import PickupMember
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.switchboard_member_user import SwitchboardMemberUser
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures

user_unpaginated_strategy = (
    joinedload(UserFeatures.agent),
    joinedload(UserFeatures.rightcall_members).selectinload(RightCallMember.rightcall),
    joinedload(UserFeatures.group_members)
    .selectinload(QueueMember.group)
    .selectinload(GroupFeatures.call_pickup_interceptor_pickups)
    .options(
        selectinload(Pickup.pickupmember_user_targets).selectinload(PickupMember.user),
        selectinload(Pickup.pickupmember_group_targets)
        .selectinload(PickupMember.group)
        .selectinload(GroupFeatures.user_queue_members)
        .selectinload(QueueMember.user),
    ),
    joinedload(UserFeatures.call_pickup_interceptor_pickups).options(
        selectinload(Pickup.pickupmember_user_targets).selectinload(PickupMember.user),
        selectinload(Pickup.pickupmember_group_targets)
        .selectinload(PickupMember.group)
        .selectinload(GroupFeatures.user_queue_members)
        .selectinload(QueueMember.user),
    ),
    joinedload(UserFeatures.user_dialactions).selectinload(Dialaction.user),
    joinedload(UserFeatures.incall_dialactions)
    .selectinload(Dialaction.incall)
    .selectinload(Incall.extensions),
    joinedload(UserFeatures.user_lines).options(
        selectinload(UserLine.line).options(
            selectinload(LineFeatures.application),
            selectinload(LineFeatures.context_rel),
            selectinload(LineFeatures.endpoint_sip).options(
                selectinload(EndpointSIP._endpoint_section).selectinload(
                    EndpointSIPSection._options
                ),
                selectinload(EndpointSIP._auth_section).selectinload(
                    EndpointSIPSection._options
                ),
            ),
            selectinload(LineFeatures.endpoint_sccp),
            selectinload(LineFeatures.endpoint_custom),
            selectinload(LineFeatures.line_extensions).selectinload(
                LineExtension.extension
            ),
            selectinload(LineFeatures.user_lines).selectinload(UserLine.user),
        ),
    ),
    joinedload(UserFeatures.queue_members),
    joinedload(UserFeatures.schedule_paths).selectinload(SchedulePath.schedule),
    joinedload(UserFeatures.switchboard_member_users).selectinload(
        SwitchboardMemberUser.switchboard
    ),
    joinedload(UserFeatures.tenant),
    joinedload(UserFeatures.voicemail),
    lazyload('*'),
)


no_strategy = []
