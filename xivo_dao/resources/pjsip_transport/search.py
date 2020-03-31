# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.pjsip_transport import PJSIPTransport
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=PJSIPTransport,
    columns={
        'uuid': PJSIPTransport.uuid,
        'name': PJSIPTransport.name,
    },
    search={'name': PJSIPTransport.name},
    default_sort='name',
)
transport_search = SearchSystem(config)
