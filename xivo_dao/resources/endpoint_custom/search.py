# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+


from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=UserCustom,
                      columns={'id': UserCustom.id,
                               'interface': UserCustom.interface,
                               'context': UserCustom.context},
                      default_sort='interface')

custom_search = SearchSystem(config)
