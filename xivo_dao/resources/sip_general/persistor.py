# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.staticsip import StaticSIP


class SIPGeneralPersistor(object):

    def __init__(self, session):
        self.session = session

    def find_by(self, **kwargs):
        query = self.session.query(StaticSIP).filter_by(**kwargs)
        return query.first()

    def find_all(self):
        query = (self.session.query(StaticSIP)
                 .filter(StaticSIP.var_name != 'register')
                 .filter(StaticSIP.var_val != None)  # noqa
                 .order_by(StaticSIP.var_metric.asc()))
        return query.all()

    def edit_all(self, sip_general):
        self.session.query(StaticSIP).filter(StaticSIP.var_name != 'register').delete()
        self.session.add_all(self._fill_default_values(sip_general))
        self.session.flush()

    def _fill_default_values(self, sip_general):
        for var_metric, setting in enumerate(sip_general):
            setting.filename = 'sip.conf'
            setting.category = 'general'
        return sip_general
