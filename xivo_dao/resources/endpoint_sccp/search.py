# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=SCCPLine,
                      columns={'id': SCCPLine.id},
                      default_sort='id')

sccp_search = SearchSystem(config)
