# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.extension import Extension
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=Extension,
                      columns={'exten': Extension.exten,
                               'context': Extension.context,
                               'feature': Extension.feature,
                               'is_feature': Extension.is_feature,
                               'type': Extension.context_type},
                      default_sort='exten')


extension_search = SearchSystem(config)
