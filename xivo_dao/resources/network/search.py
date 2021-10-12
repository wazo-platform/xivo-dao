# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.network import Network
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=Network,
    columns={
        'public_hostname': Network.public_hostname,
        'public_port': Network.public_port,
        'public_https': Network.public_https,
    },
    default_sort='public_hostname',
)

network_search = SearchSystem(config)
