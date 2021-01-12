# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.resources.utils.search import SearchSystem, SearchConfig


config = SearchConfig(
    table=Trunk,
    columns={
        'id': Trunk.id,
        'context': Trunk.context,
        'description': Trunk.description,
        'name': Trunk.name,
        'label': Trunk.label,
    },
    default_sort='id',
)

trunk_search = SearchSystem(config)
