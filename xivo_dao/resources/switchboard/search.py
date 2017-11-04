# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+


from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.resources.utils.search import (SearchSystem,
                                             SearchConfig)


config = SearchConfig(table=Switchboard,
                      columns={'name': Switchboard.name},
                      default_sort='name')

switchboard_search = SearchSystem(config)
