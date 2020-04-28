# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.incall import Incall
from xivo_dao.resources.utils.search import SearchSystem, SearchConfig


config = SearchConfig(
    table=Incall,
    columns={
        'id': Incall.id,
        'preprocess_subroutine': Incall.preprocess_subroutine,
        'user_id': Incall.user_id,
        'description': Incall.description,
    },
    default_sort='id',
)

incall_search = SearchSystem(config)
