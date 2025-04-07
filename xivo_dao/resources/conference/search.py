# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.conference import Conference
from xivo_dao.resources.utils.search import SearchConfig, SearchSystem

config = SearchConfig(
    table=Conference,
    columns={
        'id': Conference.id,
        'name': Conference.name,
        'preprocess_subroutine': Conference.preprocess_subroutine,
        'exten': Conference.exten,
    },
    default_sort='name',
)

conference_search = SearchSystem(config)
