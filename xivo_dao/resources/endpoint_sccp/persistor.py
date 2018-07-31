# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from functools import partial

from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers import errors, generators
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.utils.search import SearchResult

from .search import sccp_search


class SccpPersistor(object):

    def __init__(self, session):
        self.session = session

    def get(self, sccp_id):
        sccp = self.find(sccp_id)
        if not sccp:
            raise errors.not_found('SCCPEndpoint', id=sccp_id)
        return sccp

    def find(self, sccp_id):
        row = (self.session.query(SCCP)
               .filter(SCCP.id == sccp_id)
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
            sccp.name = generators.find_unused_hash(partial(self._already_exists, SCCP.name))
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
        self.session.delete(sccp)
        self.session.flush()
        self._fix_line(sccp)

    def _already_exists(self, column, data):
        return self.session.query(SCCP).filter(column == data).count() > 0

    def _fix_line(self, sccp):
        line_id = (self.session.query(Line.id)
                   .filter(Line.protocol == 'sccp')
                   .filter(Line.protocolid == sccp.id)
                   .scalar())

        if line_id:
            LineFixes(self.session).fix(line_id)
