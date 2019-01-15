# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings


class SCCPGeneralPersistor(object):

    def __init__(self, session):
        self.session = session

    def find_all(self):
        query = self.session.query(SCCPGeneralSettings)
        return query.all()

    def edit_all(self, sccp_general):
        self.session.query(SCCPGeneralSettings).delete()
        self.session.add_all(sccp_general)
        self.session.flush()
