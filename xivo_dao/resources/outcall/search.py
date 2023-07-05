# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.resources.utils.search import (SearchSystem,
                                             SearchConfig)


config = SearchConfig(table=Outcall,
                      columns={'id': Outcall.id,
                               'description': Outcall.description,
                               'name': Outcall.name,
                               'label': Outcall.label,
                               'preprocess_subroutine': Outcall.preprocess_subroutine},
                      default_sort='id')

outcall_search = SearchSystem(config)
