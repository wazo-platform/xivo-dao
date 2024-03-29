# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.incall import Incall
from xivo_dao.resources.utils.search import SearchSystem, SearchConfig


config = SearchConfig(
    table=Incall,
    columns={
        'preprocess_subroutine': Incall.preprocess_subroutine,
        'greeting_sound': Incall.greeting_sound,
        'description': Incall.description,
        'exten': Incall.exten,
    },
    default_sort='exten',
)

incall_search = SearchSystem(config)
