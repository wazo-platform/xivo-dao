# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
