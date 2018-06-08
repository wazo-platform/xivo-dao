# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.dialaction import Dialaction

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class VoicemailPersistor(CriteriaBuilderMixin):

    _search_table = Voicemail

    def __init__(self, session, voicemail_search):
        self.session = session
        self.voicemail_search = voicemail_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Voicemail)
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
        rows, total = self.voicemail_search.search(self.session, parameters)
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
