# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=CallPermission,
                      columns={'id': CallPermission.id,
                               'name': CallPermission.name,
                               'description': CallPermission.description,
                               'enabled': CallPermission.enabled,
                               'mode': CallPermission.mode},
                      default_sort='name')

call_permission_search = SearchSystem(config)
