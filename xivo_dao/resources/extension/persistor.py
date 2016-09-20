# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin
from xivo_dao.resources.extension.search import extension_search


class ExtensionPersistor(CriteriaBuilderMixin):

    _search_table = Extension

    def __init__(self, session):
        self.session = session

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def get_by(self, criteria):
        user = self.find_by(criteria)
        if not user:
            raise errors.not_found('Extension', **criteria)
        return user

    def _find_query(self, criteria):
        query = self.session.query(Extension)
        return self.build_criteria(query, criteria)

    def search(self, params):
        rows, total = extension_search.search(self.session, params)
        return SearchResult(total, rows)

    def create(self, extension):
        self.fill_default_values(extension)
        self.session.add(extension)
        self.session.flush()
        return extension

    def fill_default_values(self, extension):
        if not extension.type:
            extension.type = 'user'
        if not extension.typeval:
            extension.typeval = '0'

    def edit(self, extension):
        self.session.add(extension)
        self.session.flush()

    def delete(self, extension):
        self.session.query(Extension).filter(Extension.id == extension.id).delete()
        self.session.flush()

    def associate_incall(self, incall, extension):
        extension.type = 'incall'
        extension.typeval = str(incall.id)
        self.session.add(extension)
        self.session.flush()

    def dissociate_incall(self, incall, extension):
        extension.type = 'user'
        extension.typeval = '0'
        self.session.add(extension)
        self.session.flush()
