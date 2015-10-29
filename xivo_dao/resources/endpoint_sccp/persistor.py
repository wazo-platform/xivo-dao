# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers import errors
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.resources.endpoint_sccp.search import sccp_search


class SccpPersistor(object):

    def __init__(self, session):
        self.session = session

    def get(self, id):
        sccp = self.find(id)
        if not sccp:
            raise errors.not_found('SCCPEndpoint', id=id)
        return sccp

    def find(self, id):
        row = (self.session.query(SCCP)
               .filter(SCCP.id == id)
               .first())
        return row

    def search(self, params):
        rows, total = sccp_search.search(self.session, params)
        return SearchResult(total, rows)

    def create(self, sccp):
        self.fill_default_values(sccp)
        self.session.add(sccp)
        self.session.flush()
        return sccp

    def fill_default_values(self, sccp):
        if sccp.name is None:
            sccp.name = ''
        if sccp.context is None:
            sccp.context = ''
        if sccp.cid_name is None:
            sccp.cid_name = ''
        if sccp.cid_num is None:
            sccp.cid_num = ''

    def edit(self, sccp):
        self.session.add(sccp)
        self.session.flush()

    def delete(self, sccp):
        self.session.query(SCCP).filter(SCCP.id == sccp.id).delete()
        self.session.flush()
        self.dissociate_line(sccp)
        self.session.flush()

    def dissociate_line(self, sccp):
        line_id = (self.session.query(Line.id)
                   .filter(Line.protocol == 'sccp')
                   .filter(Line.protocolid == sccp.id)
                   .scalar())

        if line_id:
            LineFixes(self.session).fix(line_id)
