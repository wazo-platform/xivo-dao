# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.pickup import Pickup as CallPickup
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(table=CallPickup,
                      columns={'id': CallPickup.id,
                               'name': CallPickup.name,
                               'description': CallPickup.description,
                               'enabled': CallPickup.enabled},
                      search=['name',
                              'description'],
                      default_sort='name')

call_pickup_search = SearchSystem(config)
