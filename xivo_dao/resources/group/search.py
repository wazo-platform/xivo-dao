# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group
from xivo_dao.resources.utils.search import SearchSystem, SearchConfig


config = SearchConfig(
    table=Group,
    columns={
        'id': Group.id,
        'name': Group.name,
        'label': Group.label,
        'preprocess_subroutine': Group.preprocess_subroutine,
        'exten': Group.exten,
    },
    default_sort='label',
)

group_search = SearchSystem(config)
