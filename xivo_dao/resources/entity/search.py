# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.entity import Entity
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=Entity,
                      columns={'id': Entity.id,
                               'name': Entity.name,
                               'display_name': Entity.display_name,
                               'description': Entity.description},
                      default_sort='name')

entity_search = SearchSystem(config)
