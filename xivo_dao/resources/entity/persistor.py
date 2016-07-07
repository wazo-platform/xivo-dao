# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.alchemy.entity import Entity

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult


class EntityPersistor(object):

    def __init__(self, session, entity_search):
        self.session = session
        self.entity_search = entity_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Entity)
        for name, value in criteria.iteritems():
            column = self._get_column(name)
            query = query.filter(column == value)
        return query

    def _get_column(self, name):
        column = getattr(Entity, name, None)
        if column is None:
            raise errors.unknown(name)
        return column

    def get_by(self, criteria):
        entity = self.find_by(criteria)
        if not entity:
            raise errors.not_found('Entity', **criteria)
        return entity

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.entity_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, entity):
        self.session.add(entity)
        self.session.flush()
        return entity

    def edit(self, entity):
        self.session.add(entity)
        self.session.flush()

    def delete(self, entity):
        self.session.delete(entity)
        self.session.flush()