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

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.alchemy.staticiax import StaticIAX
from xivo_dao.alchemy.staticsip import StaticSIP
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class TrunkPersistor(CriteriaBuilderMixin):

    _search_table = Trunk

    def __init__(self, session, trunk_search):
        self.session = session
        self.trunk_search = trunk_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Trunk)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        trunk = self.find_by(criteria)
        if not trunk:
            raise errors.not_found('Trunk', **criteria)
        return trunk

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.trunk_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, trunk):
        self.session.add(trunk)
        self.session.flush()
        return trunk

    def edit(self, trunk):
        self.session.add(trunk)
        self.session.flush()

    def delete(self, trunk):
        if trunk.protocol == 'sip':
            (self.session
             .query(UserSIP)
             .filter(UserSIP.id == trunk.protocolid)
             .delete())
            if trunk.registerid:
                (self.session
                 .query(StaticSIP)
                 .filter(StaticSIP.id == trunk.registerid)
                 .delete())
        elif trunk.protocol == 'iax':
            (self.session
             .query(UserIAX)
             .filter(UserIAX.id == trunk.protocolid)
             .delete())
            if trunk.registerid:
                (self.session
                 .query(StaticIAX)
                 .filter(StaticIAX.id == trunk.registerid)
                 .delete())
        elif trunk.protocol == 'custom':
            (self.session
             .query(UserCustom)
             .filter(UserCustom.id == trunk.protocolid)
             .delete())
        self.session.delete(trunk)
        self.session.flush()
