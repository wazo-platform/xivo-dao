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

import random

from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin
from xivo_dao.resources.line.search import line_search


class LinePersistor(CriteriaBuilderMixin):

    _search_table = Line

    def __init__(self, session):
        self.session = session

    def search(self, params):
        rows, total = line_search.search_from_query(self.query(), params)
        return SearchResult(total, rows)

    def get(self, line_id):
        line = self.find(line_id)
        if not line:
            raise errors.not_found('Line', id=line_id)
        return line

    def find(self, line_id):
        return self.query().filter(Line.id == line_id).first()

    def query(self):
        return (self.session
                .query(Line)
                .options(joinedload(Line.sip_endpoint))
                .options(joinedload(Line.sccp_endpoint)))

    def find_by(self, criteria):
        query = self.build_criteria(self.query(), criteria)
        return query.first()

    def find_all_by(self, criteria):
        query = self.build_criteria(self.query(), criteria)
        return query.all()

    def create(self, line):
        if line.provisioning_code is None:
            line.provisioning_code = self.generate_provisioning_code()
        if line.configregistrar is None:
            line.configregistrar = 'default'
        if line.ipfrom is None:
            line.ipfrom = ''

        self.session.add(line)
        self.session.flush()
        return line

    def edit(self, line):
        self.session.add(line)
        self.session.flush()

    def delete(self, line):
        if line.protocol == 'sip':
            (self.session
             .query(UserSIP)
             .filter(UserSIP.id == line.protocolid)
             .delete())
        elif line.protocol == 'sccp':
            (self.session
             .query(SCCPLine)
             .filter(SCCPLine.id == line.protocolid)
             .delete())
        elif line.protocol == 'custom':
            (self.session
             .query(UserCustom)
             .filter(UserCustom.id == line.protocolid)
             .delete())
        self.session.delete(line)
        self.session.flush()

    def generate_provisioning_code(self):
        exists = True
        while exists:
            code = self.random_code()
            exists = (self.session
                      .query(Line.provisioningid)
                      .filter(Line.provisioningid == int(code))
                      .count()) > 0
        return code

    def random_code(self):
        numrange = range(1, 9)
        sequence = (str(random.choice(numrange)) for _ in range(6))
        return ''.join(sequence)
