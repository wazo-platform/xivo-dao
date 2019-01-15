# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.dialaction import Dialaction

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class VoicemailPersistor(CriteriaBuilderMixin):

    _search_table = Voicemail

    def __init__(self, session, voicemail_search, tenant_uuids=None):
        self.session = session
        self.voicemail_search = voicemail_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Voicemail)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        voicemail = self.find_by(criteria)
        if not voicemail:
            raise errors.not_found('Voicemail', **criteria)
        return voicemail

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.voicemail_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.voicemail_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, voicemail):
        self.session.add(voicemail)
        self.session.flush()
        return voicemail

    def edit(self, voicemail):
        self.session.add(voicemail)
        self.session.flush()

    def delete(self, voicemail):
        self._delete_associations(voicemail)
        self.session.delete(voicemail)
        self.session.flush()

    def _delete_associations(self, voicemail):
        (self.session.query(Dialaction)
         .filter(Dialaction.action == 'voicemail')
         .filter(Dialaction.actionarg1 == str(voicemail.id))
         .update({'linked': 0}))

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Voicemail.tenant_uuid.in_(self.tenant_uuids))
