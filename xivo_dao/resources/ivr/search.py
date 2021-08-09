# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.sql.expression import and_, cast
from sqlalchemy.sql.sqltypes import String
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.resources.utils.search import (SearchSystem,
                                             SearchConfig)


config = SearchConfig(table=IVR,
                      columns={'id': IVR.id,
                               'name': IVR.name,
                               'description': IVR.description,
                               'exten': Incall.exten},
                      search=['id',
                              'name',
                              'description',
                              'exten'],
                      sort=['id',
                            'name',
                            'description'],
                      default_sort='id')


class IVRSearchSystem(SearchSystem):

    def _search_on_extension(self, query):
        return (
            query
            .outerjoin(Dialaction, and_(Dialaction.action == 'ivr',
                                        Dialaction.actionarg1 == cast(IVR.id, String)))
            .outerjoin(Incall, and_(Dialaction.category == 'incall',
                                    Dialaction.categoryval == cast(Incall.id, String),
                                    Incall.commented == 0))
            .group_by(IVR)
        )

    def search_from_query(self, query, parameters):
        query = self._search_on_extension(query)
        return super(IVRSearchSystem, self,).search_from_query(query, parameters)


ivr_search = IVRSearchSystem(config)
