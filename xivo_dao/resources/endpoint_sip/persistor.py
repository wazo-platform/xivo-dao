# -*- coding: utf-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from functools import partial

from xivo_dao.alchemy.usersip import UserSIP as SIP
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.helpers import errors, generators
from xivo_dao.resources.endpoint_sip.search import sip_search
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class SipPersistor(CriteriaBuilderMixin):

    _search_table = SIP

    def __init__(self, session):
        self.session = session

    def find_by(self, criteria):
        return self.find_query(criteria).first()

    def find_all_by(self, criteria):
        return self.find_query(criteria).all()

    def find_query(self, criteria):
        query = self.session.query(SIP)
        return self.build_criteria(query, criteria)

    def get(self, id):
        row = self.session.query(SIP).filter(SIP.id == id).first()
        if not row:
            raise errors.not_found('SIPEndpoint', id=id)
        return row

    def search(self, params):
        rows, total = sip_search.search(self.session, params)
        return SearchResult(total, rows)

    def create(self, sip):
        self.fill_default_values(sip)
        self.persist(sip)
        return self.get(sip.id)

    def persist(self, sip):
        self.session.add(sip)
        self.session.flush()
        self.session.expire(sip)

    def edit(self, sip):
        self.persist(sip)
        self._fix_associated(sip)

    def delete(self, sip):
        self.session.query(SIP).filter(SIP.id == sip.id).delete()
        self._fix_associated(sip)

    def _fix_associated(self, sip):
        line_id = (self.session.query(Line.id)
                   .filter(Line.protocol == 'sip')
                   .filter(Line.protocolid == sip.id)
                   .scalar())
        if line_id:
            LineFixes(self.session).fix(line_id)

        trunk_id = (self.session.query(Trunk.id)
                    .filter(Trunk.protocol == 'sip')
                    .filter(Trunk.protocolid == sip.id)
                    .scalar())
        if trunk_id:
            TrunkFixes(self.session).fix(trunk_id)

    def fill_default_values(self, sip):
        if sip.name is None:
            sip.name = generators.find_unused_hash(partial(self._already_exists, SIP.name))
        if sip.secret is None:
            sip.secret = generators.find_unused_hash(partial(self._already_exists, SIP.secret))
        if sip.type is None:
            sip.type = 'friend'
        if sip.host is None:
            sip.host = 'dynamic'
        if sip.category is None:
            sip.category = 'user'

    def _already_exists(self, column, data):
        return self.session.query(SIP).filter(column == data).count() > 0
