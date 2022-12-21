# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=SCCPLine,
                      columns={'id': SCCPLine.id},
                      default_sort='id')

sccp_search = SearchSystem(config)
