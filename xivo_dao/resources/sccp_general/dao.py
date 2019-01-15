# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import SCCPGeneralPersistor


@daosession
def find_all(session):
    return SCCPGeneralPersistor(session).find_all()


@daosession
def edit_all(session, sccp_general):
    SCCPGeneralPersistor(session).edit_all(sccp_general)
