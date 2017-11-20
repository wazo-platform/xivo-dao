# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.ivr import IVR
from xivo_dao.resources.utils.search import (SearchSystem,
                                             SearchConfig)


config = SearchConfig(table=IVR,
                      columns={'id': IVR.id,
                               'name': IVR.name,
                               'description': IVR.description},
                      default_sort='id')

ivr_search = SearchSystem(config)
