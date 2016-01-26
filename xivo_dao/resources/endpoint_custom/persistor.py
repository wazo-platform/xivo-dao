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

from xivo_dao.alchemy.usercustom import UserCustom as Custom
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers import errors
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.resources.endpoint_custom.search import custom_search


class CustomPersistor(object):

    def __init__(self, session):
        self.session = session

    def get(self, id):
        custom = self.session.query(Custom).filter_by(id=id).first()
        if not custom:
            raise errors.not_found('CustomEndpoint', id=id)
        return custom

    def find_query(self, criteria):
        query = self.session.query(Custom)
        for name, value in criteria.iteritems():
            column = getattr(Custom, name, None)
            if not column:
                raise errors.unknown(name)
            query = query.filter(column == value)
        return query

    def find_by(self, criteria):
        return self.find_query(criteria).first()

    def find_all_by(self, criteria):
        return self.find_query(criteria).all()

    def search(self, params):
        rows, total = custom_search.search(self.session, params)
        return SearchResult(total, rows)

    def create(self, custom):
        self.fill_default_values(custom)
        self.session.add(custom)
        self.session.flush()
        return custom

    def fill_default_values(self, custom):
        if custom.protocol is None:
            custom.protocol = 'custom'
        if custom.category is None:
            custom.category = 'user'

    def edit(self, custom):
        self.session.add(custom)
        self.session.flush()

    def delete(self, custom):
        self.session.query(Custom).filter_by(id=custom.id).delete()
        self.session.flush()
        self.dissociate_line(custom)
        self.session.flush()

    def dissociate_line(self, custom):
        line_id = (self.session.query(Line.id)
                   .filter(Line.protocol == 'custom')
                   .filter(Line.protocolid == custom.id)
                   .scalar())

        if line_id:
            LineFixes(self.session).fix(line_id)
