# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import partial
from sqlalchemy import text

from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.helpers import errors, generators
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.utils.search import SearchResult


class SccpPersistor(object):

    def __init__(self, session, sccp_search, tenant_uuids=None):
        self.session = session
        self.sccp_search = sccp_search
        self.tenant_uuids = tenant_uuids

    def get(self, sccp_id):
        sccp = self.find(sccp_id)
        if not sccp:
            raise errors.not_found('SCCPEndpoint', id=sccp_id)
        return sccp

    def find(self, sccp_id):
        query = self.session.query(SCCP).filter(SCCP.id == sccp_id)
        query = self._filter_tenant_uuid(query)
        return query.first()

    def search(self, parameters):
        query = self.session.query(self.sccp_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.sccp_search.search_from_query(query, parameters)
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

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(SCCP.tenant_uuid.in_(self.tenant_uuids))

    def _already_exists(self, column, data):
        return self.session.query(SCCP).filter(column == data).count() > 0

    def _fix_line(self, sccp):
        line_id = (self.session.query(Line.id)
                   .filter(Line.endpoint_sccp_id == sccp.id)
                   .scalar())

        if line_id:
            LineFixes(self.session).fix(line_id)
