# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+


from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=Trunk,
                      columns={'id': Trunk.id,
                               'context': Trunk.context,
                               'description': Trunk.description},
                      default_sort='id')

trunk_search = SearchSystem(config)
