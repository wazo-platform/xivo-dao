# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+


from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=UserSIP,
                      columns={'username': UserSIP.name,
                               'type': UserSIP.type,
                               'host': UserSIP.host},
                      default_sort='username')

sip_search = SearchSystem(config)
