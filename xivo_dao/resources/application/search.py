# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.application import Application
from xivo_dao.resources.utils.search import SearchSystem, SearchConfig


config = SearchConfig(
    table=Application,
    columns={
        'uuid': Application.uuid,
        'name': Application.name,
    },
    default_sort='uuid',
)

application_search = SearchSystem(config)
