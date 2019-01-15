# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits


class IAXCallNumberLimitsPersistor(object):

    def __init__(self, session):
        self.session = session

    def find_all(self):
        query = self.session.query(IAXCallNumberLimits)
        return query.all()

    def edit_all(self, iax_callnumberlimits):
        self.session.query(IAXCallNumberLimits).delete()
        self.session.add_all(iax_callnumberlimits)
        self.session.flush()
