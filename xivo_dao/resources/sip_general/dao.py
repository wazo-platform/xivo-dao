# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import SIPGeneralPersistor


@daosession
def find_by(session, **kwargs):
    return SIPGeneralPersistor(session).find_by(**kwargs)


@daosession
def find_all(session):
    return SIPGeneralPersistor(session).find_all()


@daosession
def edit_all(session, sip_general):
    SIPGeneralPersistor(session).edit_all(sip_general)
