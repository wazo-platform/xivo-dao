# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.extension import Extension
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=Extension,
    columns={
        'exten': Extension.exten,
        'context': Extension.context,
        'type': Extension.context_type,
    },
    default_sort='exten',
)


extension_search = SearchSystem(config)
