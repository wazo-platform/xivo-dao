# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr import IVR

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class IVRPersistor(CriteriaBuilderMixin):

    _search_table = IVR

    def __init__(self, session, ivr_search):
        self.session = session
        self.ivr_search = ivr_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(IVR)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        ivr = self.find_by(criteria)
        if not ivr:
            raise errors.not_found('IVR', **criteria)
        return ivr

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.ivr_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, ivr):
        self.session.add(ivr)
        self.session.flush()
        return ivr

    def edit(self, ivr):
        self.session.add(ivr)
        self.session.flush()

    def delete(self, ivr):
        self._delete_associations(ivr)
        self.session.delete(ivr)
        self.session.flush()

    def _delete_associations(self, ivr):
        # "unlink" dialactions that points on this IVR
        (self.session.query(Dialaction)
         .filter(Dialaction.action == 'ivr')
         .filter(Dialaction.actionarg1 == str(ivr.id))
         .update({'linked': 0}))
