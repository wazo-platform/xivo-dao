# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random

from sqlalchemy import text
from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin
from xivo_dao.resources.line.search import line_search


class LinePersistor(CriteriaBuilderMixin):

    _search_table = Line

    def __init__(self, session, tenant_uuids=None):
        self.session = session
        self.tenant_uuids = tenant_uuids

    def search(self, params):
        query = self._search_query()
        query = self._filter_tenant_uuid(query)
        rows, total = line_search.search_from_query(query, params)
        return SearchResult(total, rows)

    def _search_query(self):
        return (self.session
                .query(Line)
                .options(joinedload('context_rel'))
                .options(joinedload('endpoint_sccp'))
                .options(joinedload('endpoint_sip')
                         .joinedload('context'))
                .options(joinedload('endpoint_sip')
                         .joinedload('_auth_section'))
                .options(joinedload('endpoint_sip')
                         .joinedload('_endpoint_section'))
                .options(joinedload('endpoint_custom'))
                .options(joinedload('line_extensions')
                         .joinedload('extension'))
                .options(joinedload('user_lines')
                         .joinedload('user')))

    def get(self, line_id):
        line = self.find(line_id)
        if not line:
            raise errors.not_found('Line', id=line_id)
        return line

    def find(self, line_id):
        return self.query().filter(Line.id == line_id).first()

    def query(self):
        query = (
            self.session.query(Line)
            .options(joinedload('endpoint_sccp'))
            .options(joinedload('endpoint_sip'))
        )
        query = self._filter_tenant_uuid(query)
        return query

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
        if line.endpoint_sip_uuid:
            (self.session
             .query(EndpointSIP)
             .filter(EndpointSIP.uuid == line.endpoint_sip_uuid)
             .delete())
        elif line.endpoint_sccp_id:
            (self.session
             .query(SCCPLine)
             .filter(SCCPLine.id == line.endpoint_sccp_id)
             .delete())
        elif line.endpoint_custom_id:
            (self.session
             .query(UserCustom)
             .filter(UserCustom.id == line.endpoint_custom_id)
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
        return str(100000 + random.randint(0, 899999))

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Line.tenant_uuid.in_(self.tenant_uuids))

    def associate_endpoint_sip(self, line, endpoint):
        if line.protocol not in ('sip', None):
            raise errors.resource_associated(
                'Trunk', 'Endpoint', line_id=line.id, protocol=line.protocol
            )
        line.endpoint_sip_uuid = endpoint.uuid
        self.session.flush()
        self.session.expire(line, ['endpoint_sip'])

    def dissociate_endpoint_sip(self, line, endpoint):
        if endpoint is line.endpoint_sip:
            line.endpoint_sip_uuid = None
            self.session.flush()
            self.session.expire(line, ['endpoint_sip'])

    def associate_endpoint_sccp(self, line, endpoint):
        if line.protocol not in ('sccp', None):
            raise errors.resource_associated(
                'Trunk', 'Endpoint', line_id=line.id, protocol=line.protocol
            )
        line.endpoint_sccp_id = endpoint.id
        self.session.flush()
        self.session.expire(line, ['endpoint_sccp'])

    def dissociate_endpoint_sccp(self, line, endpoint):
        if endpoint is line.endpoint_sccp:
            line.endpoint_sccp_id = None
            self.session.flush()
            self.session.expire(line, ['endpoint_sccp'])

    def associate_endpoint_custom(self, line, endpoint):
        if line.protocol not in ('custom', None):
            raise errors.resource_associated(
                'Trunk', 'Endpoint', line_id=line.id, protocol=line.protocol
            )
        line.endpoint_custom_id = endpoint.id
        self.session.flush()
        self.session.expire(line, ['endpoint_custom'])

    def dissociate_endpoint_custom(self, line, endpoint):
        if endpoint is line.endpoint_custom:
            line.endpoint_custom_id = None
            self.session.flush()
            self.session.expire(line, ['endpoint_custom'])

    def associate_application(self, line, application):
        line.application_uuid = application.uuid
        self.session.flush()

    def dissociate_application(self, line, application):
        line.application_uuid = None
        self.session.flush()
