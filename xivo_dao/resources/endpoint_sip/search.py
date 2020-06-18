# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(
    table=EndpointSIP,
    columns={
        'name': EndpointSIP.name,
        'asterisk_id': EndpointSIP.asterisk_id,
        'label': EndpointSIP.label
    },
    default_sort='label',
)

sip_search = SearchSystem(config)
