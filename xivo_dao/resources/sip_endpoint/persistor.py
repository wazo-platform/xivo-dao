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

import string
import random

from xivo_dao.alchemy.usersip import UserSIP as SIP
from xivo_dao.helpers import errors
from xivo_dao.resources.sip_endpoint.search import sip_search
from xivo_dao.resources.utils.search import SearchResult


class SipPersistor(object):

    def __init__(self, session):
        self.session = session

    def find_by(self, name, value):
        column = getattr(SIP, name, None)
        if not column:
            raise errors.unknown(name)

        row = self.session.query(SIP).filter(column == value).first()
        return self.detach(row)

    def get(self, id):
        row = self.session.query(SIP).filter(SIP.id == id).first()
        if not row:
            raise errors.not_found('SIPEndpoint', id=id)
        return self.detach(row)

    def search(self, params):
        rows, total = sip_search.search(self.session, params)
        return SearchResult(total, rows)

    def create(self, sip):
        self.fill_default_values(sip)
        self.session.add(sip)
        self.session.flush()
        self.detach(sip)
        return self.get(sip.id)

    def edit(self, sip):
        self.session.add(sip)
        self.session.flush()
        self.detach(sip)

    def delete(self, sip):
        self.session.query(SIP).filter(SIP.id == sip.id).delete()
        self.session.flush()

    def detach(self, row):
        if row:
            self.session.expunge(row)
        return row

    def fill_default_values(self, sip):
        if sip.username is None:
            sip.username = self.find_hash(SIP.username)
        if sip.secret is None:
            sip.secret = self.find_hash(SIP.secret)
        if sip.type is None:
            sip.type = 'friend'
        if sip.host is None:
            sip.host = 'dynamic'
        if sip.category is None:
            sip.category = 'user'
        sip.name = sip.username

    def find_hash(self, column):
        exists = True
        while exists:
            data = self.generate_hash()
            exists = (self.session.query(SIP)
                      .filter(column == data)
                      .count()) > 0
        return data

    def generate_hash(self, length=8):
        pool = string.lowercase + string.digits
        return ''.join(random.choice(pool) for _ in range(length))
