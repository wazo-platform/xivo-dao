# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import IAXCallNumberLimitsPersistor


@daosession
def find_all(session):
    return IAXCallNumberLimitsPersistor(session).find_all()


@daosession
def edit_all(session, iax_callnumberlimits):
    IAXCallNumberLimitsPersistor(session).edit_all(iax_callnumberlimits)
