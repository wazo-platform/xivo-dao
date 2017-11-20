# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group
from xivo_dao.resources.utils.search import (SearchSystem,
                                             SearchConfig)


config = SearchConfig(table=Group,
                      columns={'id': Group.id,
                               'name': Group.name,
                               'preprocess_subroutine': Group.preprocess_subroutine},
                      default_sort='id')

group_search = SearchSystem(config)
