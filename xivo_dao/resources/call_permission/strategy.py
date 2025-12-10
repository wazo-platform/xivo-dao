# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import selectinload

from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.userfeatures import UserFeatures

preload_relationships = (
    selectinload(CallPermission.rightcall_groups)
    .selectinload(RightCallMember.group)
    .load_only(GroupFeatures.uuid, GroupFeatures.id, GroupFeatures.name),
    selectinload(CallPermission.rightcall_users)
    .selectinload(RightCallMember.user)
    .load_only(UserFeatures.uuid, UserFeatures.firstname, UserFeatures.webi_lastname),
    selectinload(CallPermission.rightcall_outcalls)
    .selectinload(RightCallMember.outcall)
    .load_only(Outcall.id, Outcall.name),
    selectinload(CallPermission.rightcallextens),
)
