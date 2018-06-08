# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.staticiax import StaticIAX


class IAXGeneralPersistor(object):

    def __init__(self, session):
        self.session = session

    def find_all(self):
        query = (self.session.query(StaticIAX)
                 .filter(StaticIAX.var_name != 'register')
                 .filter(StaticIAX.var_val != None)  # noqa
                 .order_by(StaticIAX.var_metric.asc()))
        return query.all()

    def edit_all(self, iax_general):
        self.session.query(StaticIAX).filter(StaticIAX.var_name != 'register').delete()
        self.session.add_all(self._fill_default_values(iax_general))
        self.session.flush()

    def _fill_default_values(self, iax_general):
        for var_metric, setting in enumerate(iax_general):
            setting.filename = 'iax.conf'
            setting.category = 'general'
        return iax_general
