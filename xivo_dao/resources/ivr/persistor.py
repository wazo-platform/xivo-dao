# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class IVRPersistor(CriteriaBuilderMixin):

    _search_table = IVR

    def __init__(self, session, ivr_search, tenant_uuids=None):
        self.session = session
        self.ivr_search = ivr_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(IVR)
        query = self._filter_tenant_uuid(query)
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

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(IVR.tenant_uuid.in_(self.tenant_uuids))

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
