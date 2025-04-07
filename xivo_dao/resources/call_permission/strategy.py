# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import selectinload

from xivo_dao.alchemy.rightcall import RightCall as CallPermission

preload_relationships = (
    selectinload(CallPermission.rightcall_groups)
    .selectinload('group')
    .load_only('uuid', 'id', 'name'),
    selectinload(CallPermission.rightcall_users)
    .selectinload('user')
    .load_only('uuid', 'firstname', 'webi_lastname'),
    selectinload(CallPermission.rightcall_outcalls)
    .selectinload('outcall')
    .load_only('id', 'name'),
    selectinload(CallPermission.rightcallextens),
)
