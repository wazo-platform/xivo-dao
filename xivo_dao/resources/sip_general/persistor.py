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

from xivo_dao.alchemy.staticsip import StaticSIP


class SIPGeneralPersistor(object):

    def __init__(self, session):
        self.session = session

    def find_all(self):
        query = self.session.query(StaticSIP).order_by(StaticSIP.var_metric.asc())
        return query.all()

    def edit_all(self, sip_general):
        self.session.query(StaticSIP).delete()
        self.session.add_all(self._update_order(sip_general))
        self.session.flush()

    def _update_order(self, sip_general):
        for var_metric, setting in enumerate(sip_general):
            setting.var_metric = var_metric
            setting.filename = 'sip.conf'
            setting.category = 'general'
        return sip_general
