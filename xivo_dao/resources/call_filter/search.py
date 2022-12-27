# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.callfilter import Callfilter as CallFilter
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(table=CallFilter,
                      columns={'id': CallFilter.id,
                               'name': CallFilter.name,
                               'description': CallFilter.description},
                      default_sort='name')

call_filter_search = SearchSystem(config)
