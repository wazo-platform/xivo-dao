# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import joinedload
from xivo_dao.alchemy.rightcall import RightCall as CallPermission


call_permission_preload_relationships = (
    joinedload(CallPermission.rightcall_groups)
    .joinedload('group')
    .load_only('uuid', 'id', 'name'),
    joinedload(CallPermission.rightcall_users)
    .joinedload('user')
    .load_only('uuid', 'firstname', 'webi_lastname'),
    joinedload(CallPermission.rightcall_outcalls)
    .joinedload('outcall')
    .load_only('id', 'name'),
    joinedload(CallPermission.rightcallextens),
)
