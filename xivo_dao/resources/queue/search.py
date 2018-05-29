# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.resources.utils.search import SearchSystem, SearchConfig


config = SearchConfig(table=QueueFeatures,
                      columns={'id': QueueFeatures.id,
                               'name': QueueFeatures.name,
                               'preprocess_subroutine': QueueFeatures.preprocess_subroutine},
                      default_sort='id')

queue_search = SearchSystem(config)
